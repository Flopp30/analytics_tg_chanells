import asyncio
import itertools
from datetime import datetime
from pprint import pprint

from asgiref.sync import sync_to_async
from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand, CommandError
from telethon import TelegramClient

from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest
from telethon.tl.types import (
    InputPeerEmpty,
    PeerChannel,
    Channel as TG_CHANNEL,
    Message as TG_MESSAGE
)
from django.conf import settings
from message.models import Message as DJ_MESSAGE
from channel.models import Channel as DJ_CHANNEL


class Command(BaseCommand):
    help = '''
    Run scrapping bot. 
    Phone, api id and api hash can be added in arguments (--phone --api_id --api_hash) or set in 
    env variables (TG_PHONE_NUMBER, TG_API_ID, TG_API_HASH)
    '''

    def add_arguments(self, parser):
        parser.add_argument('--phone', help='phone number')
        parser.add_argument('--api_id', help='api id')
        parser.add_argument('--api_hash', help='api hash')

    def handle(self, *args, **options):
        phone = options.get('phone') or settings.TG_PHONE_NUMBER
        api_id = options.get('api_id') or settings.TG_API_ID
        api_hash = options.get('api_hash') or settings.TG_API_HASH
        if not phone or not api_id or not api_hash:
            raise CommandError(
                'Please, set TG_PHONE_NUMBER, TG_API_ID and TG_API_HASH '
                'in environment variables or add with command arguments'
            )

        asyncio.run(main(phone, int(api_id), api_hash))


async def main(phone: str, api_id: int, api_hash: str):
    client = TelegramClient(phone, api_id, api_hash)
    async with client:
        await scrapping(client)


async def scrapping(client: TelegramClient):
    # views
    # reactions
    # forwards ?
    channels = await get_channels(client)
    tasks = [asyncio.create_task(get_ch_messages(client, ch)) for ch in channels]
    res = await asyncio.gather(*tasks)
    updated_messages = []
    is_updated = False
    for messages_by_channel_id in res:
        for ch_id, messages in messages_by_channel_id.items():
            for message in messages:
                dj_message, is_created = await DJ_MESSAGE.objects.aget_or_create(
                    channel_id=ch_id,
                    pk=message.get('id'),
                    defaults={
                        "text": message.get('message'),
                        "views": message.get('views'),
                        "forwards": message.get('forwards'),
                        "reactions": get_reactions_count(message),
                    }
                )
                if not is_created:
                    if dj_message.text != message.get('message'):
                        dj_message.text = message.get('message')
                        is_updated = True

                    if dj_message.views != message.get('views'):
                        dj_message.views = message.get('views')
                        is_updated = True

                    if dj_message.forwards != message.get('forwards'):
                        dj_message.forwards = message.get('forwards')
                        is_updated = True

                    if dj_message.reactions != get_reactions_count(message):
                        dj_message.reactions = get_reactions_count(message)
                        is_updated = True

                    if is_updated:
                        updated_messages.append(dj_message)
                    is_updated = False
        await DJ_MESSAGE.objects.abulk_update(updated_messages, ('text', 'forwards', 'views', 'reactions'))


async def get_channels(client: TelegramClient) -> [TG_CHANNEL]:
    last_date = None
    size_chats = 200
    result = await client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=size_chats,
        hash=0
    ))
    tg_channels_by_ids = {ch.id: ch for ch in result.chats if isinstance(ch, TG_CHANNEL)}
    await create_new_channels_in_db(tg_channels_by_ids)
    return tg_channels_by_ids.values()


async def create_new_channels_in_db(tg_ch_by_id: {int: TG_CHANNEL}):
    new_channels = []
    existing_channels = DJ_CHANNEL.objects.values_list('pk', flat=True)
    existing_pks = []
    async for pk in existing_channels:
        existing_pks.append(pk)
    for tg_channel_id, tg_channel in tg_ch_by_id.items():
        if tg_channel_id not in existing_pks:
            new_channels.append(
                DJ_CHANNEL(
                    pk=tg_channel_id,
                    name=tg_channel.title
                )
            )
    await DJ_CHANNEL.objects.abulk_create(new_channels)


async def get_ch_messages(client: TelegramClient, target_ch: TG_CHANNEL) -> {int: [TG_MESSAGE]}:
    all_messages = []
    offset_id = 0
    limit = 3
    total_messages = 0
    total_count_limit = 0
    while True:
        history = await client(GetHistoryRequest(
            peer=target_ch,
            offset_id=offset_id,
            # offset_date=datetime.now() - relativedelta(days=1),  # yesterday
            # offset_date=datetime.now(),  # today
            offset_date=None,  # all
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break
        messages = []
        for message in history.messages:
            if isinstance(message, TG_MESSAGE):
                all_messages.append(message.to_dict())
        # offset_id = messages[len(messages) - 1].id
        # if total_count_limit != 0 and total_messages >= total_count_limit:
        #     break
        break
    return {target_ch.id: all_messages}


def get_reactions_count(message: dict):
    if (reactions_dict := message.get('reactions')):
        if (res := reactions_dict.get('results')):
            try:
                return res[0].get('count')
            except (IndexError, KeyError):
                return 0
    return 0
