from telebot.async_telebot import AsyncTeleBot
from telebot.types import (
    Message,
    InlineKeyboardButton as IKB,
    InlineKeyboardMarkup as IKM
)

from dotenv import load_dotenv
from os import getenv


load_dotenv()
bot = AsyncTeleBot(token=getenv('BOT_TOKEN'))


class Keys:
    cancelQuestionButton = IKM(
        IKB(text='❌ Отмена', callback_data='cancelQuestion')
    )


@bot.message_handler(commands=['/start'])
async def startCommand(message: Message) -> None:
    command = message.text.split(' ')
    if command >= 2 and command[1].isdigit():
        bot.send_message(
            message.chat.id,
            'Задайте свой вопрос:\n'
            'Для отмены нажмите кнопку "❌ Отмена".'
        )
        return bot.register_message_handler()


async def getQuestion(message: Message) -> any:
    ...