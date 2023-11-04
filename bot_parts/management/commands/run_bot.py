from django.core.management import BaseCommand, CommandError
from telethon.sync import TelegramClient

import csv

from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from django.conf import settings


class Command(BaseCommand):
    help = '''
    Run scrapping bot. Phone, api id and api hash can be added in arguments (--phone --api_id --api_hash) or set in 
    env variables
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

        bot_part(phone, api_id, api_hash)


def bot_part(phone, api_id, api_hash):
    client = TelegramClient(phone, api_id, api_hash)
    client.start()
