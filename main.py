from telebot.async_telebot import AsyncTeleBot
from telebot.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton as IKB,
    InlineKeyboardMarkup as IKM
)

from dotenv import load_dotenv
from os import getenv

from database import dloadQuestion, setState, getState, getRow
from logger import Logger


load_dotenv()
bot = AsyncTeleBot(token=getenv('BOT_TOKEN'))
logger = Logger()


class Keys:
    cancelQuestionButton = IKM(
        IKB(text='❌ Отмена', callback_data='cancelQuestion')
    )


@bot.message_handler(commands=['/start'])
async def startCommand(message: Message) -> None:
    command = message.text.split(' ')
    if command >= 2 and command[1].isdigit():
        await bot.send_message(
            message.chat.id,
            'Задайте свой вопрос:\n'
            'Для отмены нажмите кнопку "❌ Отмена".'
        )
        return await setState(
            message.from_user.id, 'question', int(command[1])
        )

    await bot.send_message(
        message.from_user.id,
        '👋 Добро пожаловать в бота для получения анонимных вопросов,'
        f' <a href=tg://user?id={message.from_user.id}>{message.from_user.full_name}</a>!\n'
        'С помощью данного бота вы можете получать вопросы, а также отправлять их. '
        'Для получения вопросов необходимо опубликовать вашу ссылку. После её публикации, '
        'перешедший по ней сможет написать вам вопрос\n\n'
        '📥 Ваша ссылка: '
        f'https://t.me/AnonsQuestionsRobot?start={message.from_user.id}'
    )


@bot.message_handler(content_types=['text'])
async def getQuestion(message: Message) -> any:
    other_user = await getState(message.from_user.id)
    if not other_user:
        return await startCommand(message)

    qid = await dloadQuestion(
        message.from_user.id,
        message.from_user.full_name,
        message.text,
        other_user
    )
    question_id, user_id = getRow()

    try:
        await bot.send_message(
            other_user,
            '📩 Вам задали новый вопрос!\n'
            '📃 Его текст:\n\n'
            f'<pre>{message.text}</pre>',
            parse_mode='HTML',
            reply_markup=IKM(
                [
                    IKB(text='💌 Ответить', callback_data=f'responseQuestion {question_id}'),
                    IKB(text='👁️ Кто это?', callback_data=f'whoAsked {question_id}')
                ],
                row_width=1
            )
        )

        return await bot.reply_to(
            message, '✅ Ваш вопрос был успешно отправлен! Ожидайте ответа.'
        )
    except BaseException as errorText:
        await logger.asyncLogger(
            f'Error while processing new question: {errorText}\n'
            'Other Info:\n\n'
            '<pre>'
            f'    Receiver ID: {other_user}\n'
            f'    Sender ID: {message.from_user.id}\n'
            f'    Question ID: {qid}\n'
            f'    Question text: {message.text}'
            '</pre>',
            module='WAWILON-ANONQUESTIONS'
        )

        return await bot.reply_to(
            message,
            '❌ Произошла непредвиденная ошибка при доставке вашего вопроса.'
        )


@bot.callback_query_handler(func=lambda event: event.data == 'cancelQuestion')
async def cancelQuestion(event: CallbackQuery) -> Message | bool:
    await setState(event.from_user.id, 'main')

    return await bot.edit_message_text(
        inline_message_id=event.inline_message_id,
        text='📃 Вы были возвращены в главное меню.'
    )


@bot.callback_query_handler(func=lambda event: event.data.startswith('whoAsked'))
async def whoAsked(event: CallbackQuery) -> any:
    