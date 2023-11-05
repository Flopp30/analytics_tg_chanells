from django.conf import settings
from django.db.models import Count
from telethon import TelegramClient
from telethon.tl.types import Message as TgMessage

from bot_parts.utils import get_reactions_count
from channel.models import Channel as DjChannel
from message.models import Message as DjMessage
from metrics.models import Metric


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


async def check_messages(client: TelegramClient, one_minute: bool = True):
    if one_minute:
        filter_kwargs = {
            "metrics_count__lt": 5  # 5 раз трекаем с интервалом минута
        }
    else:
        filter_kwargs = {
            "metrics_count__gte": 5,  # 10 раз трекаем с интервалом в 5 минут или 5 раз с интервалом в 10
            "metrics_count__lt": 15 if settings.STARTING_INTERVAL_SECOND_TASK == 5 else 10,
        }
    channels = (
        DjChannel.objects
        .select_related('category')
        .prefetch_related('messages')
        .annotate(messages_count=Count('messages'))
        .filter(is_tracking=True)
    )
    updated_messages = []
    updated_channels = []
    created_metrics = []
    async for dj_channel in channels:
        messages = (
            dj_channel.messages
            .prefetch_related('metrics')
            .annotate(metrics_count=Count('metrics'))
            .filter(**filter_kwargs)
        )
        mes_by_tg_ids: {int: DjMessage} = {
            mes.tg_message_id: mes
            async for mes in messages
        }

        async for tg_mes in client.iter_messages(dj_channel.chat_id, ids=list(mes_by_tg_ids.keys())):
            tg_mes: TgMessage
            dj_mes: DjMessage = mes_by_tg_ids.get(tg_mes.id)
            dj_mes.forwards = tg_mes.forwards
            dj_mes.views = tg_mes.views / 100
            dj_mes.reactions = get_reactions_count(tg_mes)

            updated_messages.append(dj_mes)
            new_metric = Metric()
            new_metric.update_from_message(dj_mes)
            created_metrics.append(new_metric)

            await _update_message_coeffs(dj_mes)
            await _update_channel_coeffs(dj_channel, updated_channels)

            if dj_channel.messages_count >= 20 and dj_mes.metrics_count == 4:
                await _forward_message(client, dj_mes, dj_channel, tg_mes)

    await Metric.objects.abulk_create(created_metrics)
    await DjMessage.objects.abulk_update(
        updated_messages,
        ['views', 'forwards', 'reactions', 'average_forward_coef', 'average_reaction_coef']
    )
    await DjChannel.objects.abulk_update(
        updated_channels,
        ['average_forward_coef', 'average_react_coef']
    )


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
    add_perc = settings.ADDITIONAL_PERCENTS_FOR_REPOST + 100
    first = dj_mes.average_reaction_coef > dj_channel.average_react_coef * add_perc
    second = dj_mes.average_forward_coef > dj_channel.average_forward_coef * add_perc

    if first or second:
        try:
            target_chat_id = int(dj_channel.category.target_chat_id)
        except (ValueError, AttributeError):
            pass
        else:
            message = (
                f"Реакции канала: {dj_channel.average_react_coef}\n"
                f"Реакции сообщения: {dj_mes.average_reaction_coef}\n\n"
                f"Репосты канала: {dj_channel.average_forward_coef}\n"
                f"Репосты сообщения: {dj_mes.average_forward_coef}\n\n"
            )
            await client.send_message(target_chat_id, message)
            await client.forward_messages(target_chat_id, tg_mes)
