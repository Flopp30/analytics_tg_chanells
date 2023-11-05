import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.db.models import Count
from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.tl.types import (
    Message as TgMessage,
)

from bot_parts import periodic_tasks
from bot_parts.models import ExternalSettings
from bot_parts.utils import get_reactions_count
from channel.models import Channel as DjChannel
from message.models import Message as DjMessage


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
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(
        periodic_tasks.check_messages,
        trigger=IntervalTrigger(minutes=1),
        kwargs={
            "client": client,
            "one_minute": True,
        }
    )
    scheduler.add_job(
        periodic_tasks.check_messages,
        trigger=IntervalTrigger(minutes=5),
        kwargs={
            "client": client,
            "one_minute": False,
        }
    )
    scheduler.add_job(
        periodic_tasks.update_uploaded_channels,
        trigger=IntervalTrigger(minutes=10),
        kwargs={
            "client": client,
        }
    )

    @client.on(NewMessage(chats='me'))
    async def reload_data(event: NewMessage.Event):
        if event.message.message == '!update_settings':
            ext_settings = await ExternalSettings.objects.afirst()
            settings_for_send = ''
            for key, value in ext_settings.__dict__.items():
                if key != 'id' and not key.startswith('_'):
                    setattr(settings, key.upper(), value)
                    settings_for_send += f"{key.upper()}: {value}\n"

            message = 'Настройки успешно вступили в силу.\n' + settings_for_send
            await client.send_message('me', message)

    @client.on(NewMessage(incoming=True))
    async def create_new_post_in_db(event: NewMessage.Event):
        tg_mes = event.message
        if event.is_channel and isinstance(tg_mes, TgMessage):
            dj_channel, _ = (
                await DjChannel.objects
                .select_related('category')
                .aget_or_create(
                    chat_id=event.chat_id,
                    defaults={
                        "name": event.chat.title,
                    }
                )
            )
            if dj_channel.is_tracking:
                dj_message, is_created = await DjMessage.objects.aget_or_create(
                    tg_message_id=tg_mes.id,
                    channel_id=dj_channel.pk,
                    defaults={
                        "text": tg_mes.message,
                        "views": tg_mes.views or 0,
                        "forwards": tg_mes.forwards or 0,
                        "reactions": get_reactions_count(tg_mes),
                    }
                )
                if not is_created:
                    dj_message.message = tg_mes.message
                    dj_message.views = tg_mes.views / 100 or 0
                    dj_message.forwards = tg_mes.forwards or 0
                    dj_message.reactions = get_reactions_count(tg_mes)

                await dj_message.asave()

    async with client:
        scheduler.start()  # run scheduler
        await periodic_tasks.update_uploaded_channels(client)  # upload new channels
        await client.run_until_disconnected()
