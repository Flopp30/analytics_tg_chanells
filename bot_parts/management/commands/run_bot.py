import asyncio
import itertools
from datetime import datetime
from pprint import pprint

from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand, CommandError
from telethon import TelegramClient

from telethon.tl.functions.messages import GetDialogsRequest, GetHistoryRequest
from telethon.tl.types import InputPeerEmpty, Channel, PeerChannel, Message
from django.conf import settings


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
    messages = list(itertools.chain.from_iterable(res))
    for mes in messages:
        pprint(mes)
        # print("mes: ", mes.get('message'))
        # print("views:", mes.get('views'))
        # print("reactions:", mes.get('reactions'))
        # print("forwards:", mes.get('forwards'))
        print('--' * 80)


async def get_channels(client: TelegramClient) -> [Channel]:
    last_date = None
    size_chats = 200
    result = await client(GetDialogsRequest(
        offset_date=last_date,
        offset_id=0,
        offset_peer=InputPeerEmpty(),
        limit=size_chats,
        hash=0
    ))
    return [ch for ch in result.chats if isinstance(ch, Channel)]


async def get_ch_messages(client: TelegramClient, target_ch: Channel) -> [Message]:
    all_messages = []
    offset_id = 0
    limit = 100
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
        messages = history.messages
        for message in messages:
            all_messages.append(message.to_dict())
        offset_id = messages[len(messages) - 1].id
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break
        break
    return all_messages
