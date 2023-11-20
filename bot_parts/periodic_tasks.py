import asyncio
import datetime
import logging
from types import NoneType

from django.conf import settings
from django.db.models import Count
from django.utils import timezone
from telethon import TelegramClient
from telethon.tl.types import Message as TgMessage

from bot_parts.utils import get_reactions_count
from channel.models import Channel as DjChannel
from message.models import Message as DjMessage
from metrics.models import Metric

logger = logging.getLogger(__name__)


async def clean_db(client: TelegramClient):
    if settings.MESSAGES_TTL != 0:
        clean_date = timezone.now() - datetime.timedelta(days=settings.MESSAGES_TTL)
        await DjMessage.objects.filter(created_at__lte=clean_date).adelete()
        await client.send_message('me', f'Сообщения и метрики старше, чем\n{clean_date} успешно удалены')


async def update_uploaded_channels(client: TelegramClient):
    tg_channels = []
    async for dialog in client.iter_dialogs():
        if dialog.is_channel:
            tg_channels.append(
                {
                    "chat_id": dialog.id,
                    "name": dialog.entity.title
                }
            )
    existing_chat_ids = [pk async for pk in DjChannel.objects.values_list('chat_id', flat=True)]
    new_dj_channels = []
    for tg_channel in tg_channels:
        if tg_channel.get('chat_id') not in existing_chat_ids:
            new_dj_channels.append(DjChannel(**tg_channel))

    await DjChannel.objects.abulk_create(new_dj_channels)


async def check_messages(client: TelegramClient, one_min: bool = True):
    filter_kwargs = _get_filter_kwargs(one_min)
    messages_datetime_tracking = timezone.now() - datetime.timedelta(hours=1, minutes=10)
    channels = (
        DjChannel.objects
        .select_related('category')
        .prefetch_related('messages')
        .annotate(messages_count=Count('messages'))
        .filter(is_tracking=True)
        .filter(messages__is_forwarded=False, messages__created_at__gte=messages_datetime_tracking)
    )
    updated_messages = []
    updated_channels = []
    created_metrics = []
    tasks = []
    async for dj_channel in channels:
        tasks.append(
            asyncio.create_task(
                channel_process(dj_channel, filter_kwargs, client, updated_messages, created_metrics, updated_channels)
            )
        )
    await asyncio.gather(*tasks)

    await Metric.objects.abulk_create(created_metrics)
    await DjMessage.objects.abulk_update(
        updated_messages,
        [
            'views', 'forwards', 'reactions', 'average_forward_coef',
            'average_reaction_coef', 'is_forwarded', 'updated_at'
        ]
    )
    await DjChannel.objects.abulk_update(
        updated_channels,
        ['average_forward_coef', 'average_react_coef']
    )


async def channel_process(
        dj_channel: DjChannel,
        filter_kwargs: dict,
        client: TelegramClient,
        updated_messages: list,
        created_metrics: list,
        updated_channels: list
):
    messages = (
        dj_channel.messages.prefetch_related('metrics')
        .annotate(metrics_count=Count('metrics'))
        .filter(**filter_kwargs)
    )

    mes_by_tg_ids: {int: DjMessage} = {
        mes.tg_message_id: mes
        async for mes in messages
    }
    async for tg_mes in client.iter_messages(dj_channel.chat_id, ids=list(mes_by_tg_ids.keys())):
        if isinstance(tg_mes, NoneType):
            continue
        dj_mes: DjMessage = mes_by_tg_ids.get(tg_mes.id)
        dj_mes.forwards = tg_mes.forwards or 0
        dj_mes.views = tg_mes.views or 0 / settings.VIEWS_DIV
        dj_mes.reactions = get_reactions_count(tg_mes)
        dj_mes.updated_at = timezone.now()

        updated_messages.append(dj_mes)
        new_metric = Metric()
        new_metric.update_from_message(dj_mes)
        created_metrics.append(new_metric)

        await _update_message_coeffs(dj_mes)
        await _update_channel_coeffs(dj_channel, updated_channels)
        await _forward_message(client, dj_mes, dj_channel, tg_mes)


async def _update_channel_coeffs(dj_channel: DjChannel, updated_channels: [DjChannel]):
    channel_messages = [m async for m in dj_channel.messages.order_by('-created_at')[:20]]
    if len(channel_messages) != 0:
        sum_react_coef = 0
        sum_forward_coef = 0
        for m in channel_messages:
            sum_react_coef += m.average_reaction_coef
            sum_forward_coef += m.average_forward_coef

        dj_channel.average_forward_coef = sum_forward_coef / len(channel_messages)
        dj_channel.average_react_coef = sum_react_coef / len(channel_messages)
        updated_channels.append(dj_channel)


async def _update_message_coeffs(dj_mes: DjMessage):
    metrics = [metric async for metric in dj_mes.metrics.all()]
    if len(metrics) != 0:
        sum_avg_reacts = 0
        sum_avg_forwards = 0
        for met in metrics:
            sum_avg_reacts += met.reaction_coef
            sum_avg_forwards += met.forwards_coef

        dj_mes.average_forward_coef = sum_avg_forwards / len(metrics)
        dj_mes.average_reaction_coef = sum_avg_reacts / len(metrics)
    else:
        dj_mes.average_forward_coef = 0
        dj_mes.average_reaction_coef = 0


async def _forward_message(
        client: TelegramClient,
        dj_mes: DjMessage,
        dj_channel: DjChannel,
        tg_mes: TgMessage
):
    first = dj_channel.messages_count >= settings.MIN_MESSAGES_COUNT_BEFORE_REPOST
    second = dj_mes.metrics_count + 1 == settings.MIN_METRICS_COUNT_BEFORE_REPOST  # added current metric

    logger.info(f'{first and second}: Message count in channel: {first}, Metric count in message: {second}')
    if first and second:

        add_perc = settings.ADDITIONAL_PERCENTS_FOR_REPOST + 100
        first = dj_mes.average_reaction_coef >= dj_channel.average_react_coef * add_perc / 100
        second = dj_mes.average_forward_coef >= dj_channel.average_forward_coef * add_perc / 100

        logger.info(f'Percent: {add_perc}')
        logger.info(f'Reactions {first}: Channel={dj_channel.average_react_coef}, Message={dj_mes.average_reaction_coef}')
        logger.info(f'Forwards {second}: Channel={dj_channel.average_forward_coef}, Message={dj_mes.average_forward_coef}')
        logger.info(f'{"-" * 30}')
        if first or second:
            try:
                target_chat_id = int(dj_channel.category.target_chat_id)
            except (ValueError, AttributeError):
                logger.warning(f'Сообщение {dj_mes.pk} не отправилось из-за ошибки')

            else:
                message = (
                    f"Реакции канала: {dj_channel.average_react_coef}\n"
                    f"Реакции сообщения: {dj_mes.average_reaction_coef}\n\n"
                    f"Репосты канала: {dj_channel.average_forward_coef}\n"
                    f"Репосты сообщения: {dj_mes.average_forward_coef}\n\n"
                )
                await client.send_message(target_chat_id, message)
                await client.forward_messages(target_chat_id, tg_mes)
                dj_mes.is_forwarded = True


def _get_filter_kwargs(one_min) -> dict:
    if one_min:
        filter_kw = {
            "metrics_count__lt": 5  # 5 раз трекаем с интервалом минута
        }
    else:
        filter_kw = {
            "metrics_count__gte": 5,  # 10 раз трекаем с интервалом в 5 минут или 5 раз с интервалом в 10
            "metrics_count__lt": 15 if settings.STARTING_INTERVAL_SECOND_TASK == 5 else 10,
        }
    return filter_kw
