from telebot.types import Message

from loader import bot
from . import help


@bot.message_handler(state=None)
def bot_echo(message: Message):
    """Обрабатывает любое сообщение, которое не является командой и переводит на функцию 'bot_help' """
    help.bot_help(message)

