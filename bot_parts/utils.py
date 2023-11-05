from telethon.tl.types import Message as TgMessage


def get_reactions_count(tg_mes: TgMessage) -> int:
    if not hasattr(tg_mes, 'reactions'):
        return 0
    if not hasattr(tg_mes.reactions, 'results'):
        return 0
    try:
        return tg_mes.reactions.results[0].count
    except (KeyError, IndexError):
        return 0
