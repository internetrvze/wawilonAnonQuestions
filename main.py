from telebot.async_telebot import AsyncTeleBot
from telebot.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton as IKB,
    InlineKeyboardMarkup as IKM
)

from dotenv import load_dotenv
from os import getenv
from json import loads
from asyncio import run as _runner

from database import dloadQuestion, setState, getState, getRow
from logger import Logger


load_dotenv()
bot = AsyncTeleBot(token=getenv('BOT_TOKEN'))
admin_ids = loads(getenv('ADMINS'))
print(admin_ids)
logger = Logger()


class Keys:
    cancelQuestionButton = IKM(
        [
            [IKB(text='❌ Отмена', callback_data='cancelQuestion')]
        ]
    )


@bot.message_handler(commands=['start'])
async def startCommand(message: Message) -> None:
    command = message.text.split(' ')
    print(command)
    if len(command) >= 2 and command[1].isdigit():
        await bot.send_message(
            message.chat.id,
            'Задайте свой вопрос:\n'
            'Для отмены нажмите кнопку "❌ Отмена".',
            reply_markup=Keys.cancelQuestionButton
        )
        return await setState(
            message.from_user.id, 'question', int(command[1])
        )

    await bot.send_message(
        message.from_user.id,
        '👋 Добро пожаловать в бота для получения анонимных вопросов,'
        f' <a href="tg://user?id={message.from_user.id}">'
        f'{message.from_user.full_name}</a>!\n'
        'С помощью данного бота вы можете получать вопросы,'
        ' а также отправлять их. Для получения вопросов необходимо '
        'опубликовать вашу ссылку. После её публикации, перешедший по ней '
        'сможет написать вам вопрос\n\n'
        '📥 Ваша ссылка: '
        f'https://t.me/AnonsQuestionsRobot?start={message.from_user.id}',
        parse_mode='HTML'
    )


@bot.message_handler(content_types=['text'])
async def getQuestion(message: Message) -> any:
    other_user, qstate = await getState(message.from_user.id)
    print(qstate)
    print(other_user)
    if not other_user:
        return await startCommand(message)

    qid = await dloadQuestion(
        message.from_user.id,
        message.from_user.full_name,
        message.text,
        other_user
    )

    if not qstate:
        try:
            await bot.send_message(
                other_user,
                '📩 Вам задали новый вопрос!\n'
                '📃 Его текст:\n\n'
                f'<pre>{message.text}</pre>',
                parse_mode='HTML',
                reply_markup=IKM(
                    [
                        [
                            IKB(
                                text='💌 Ответить',
                                callback_data=f'responseQuestion {qid}'
                            )
                        ],
                        [
                            IKB(
                                text='👁️ Кто это?',
                                callback_data=f'whoAsked {qid}'
                            )
                        ]
                    ],
                )
            )

            await bot.reply_to(
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

            await bot.reply_to(
                message,
                '❌ Произошла непредвиденная ошибка '
                'при доставке вашего вопроса.'
            )
        return await setState(
            message.from_user.id, 'main'
        )
    user = message.from_user
    try:
        await bot.send_message(
            other_user,
            '📩 Вам поступил ответ от пользователя '
            f'<a href="tg://user?id={user.id}">{user.full_name}</a>!\n'
            '📃 Его текст:\n\n'
            f'<pre>{message.text}</pre>',
            parse_mode='HMTL'
        )

        await bot.reply_to(
            message, '✅ Ответ на вопрос был успешно доставлен!'
        )

    except BaseException as errorText:
        await logger.asyncLogger(
            f'Error while processing new answer: {errorText}\n'
            'Other Info:\n\n'
            '<pre>'
            f'    Receiver ID: {other_user}\n'
            f'    Sender ID: {message.from_user.id}\n'
            f'    Question ID: {qid}\n'
            f'    Question text: {message.text}'
            '</pre>',
            module='WAWILON-ANONQUESTIONS'
        )

        await bot.reply_to(
            message,
            '❌ Произошла непредвиденная ошибка '
            'при доставке вашего ответа на вопрос.'
        )
    return await setState(
        message.from_user.id, 'main'
    )

@bot.callback_query_handler(func=lambda event: event.data == 'cancelQuestion')
async def cancelQuestion(event: CallbackQuery) -> None:
    await setState(event.from_user.id, 'main')

    await bot.delete_message(
        chat_id=event.chat_instance,
        message_id=event.message.id
    )

    await bot.send_message(
        chat_id=event.chat_instance,
        text='📃 Вы были возвращены в главное меню.'
    )

    return await startCommand(event.message)


@bot.callback_query_handler(
        func=lambda event: event.data.startswith('whoAsked')
)
async def whoAsked(event: CallbackQuery) -> any:
    if event.from_user.id not in admin_ids:
        return await bot.answer_callback_query(
            event.id, text='Пошёл нахуй отсюдава🗿', show_alert=True
        )
    row = (
        await getRow(
            int(event.data.split(' ')[1])
        )
    )

    user = (await bot.get_chat_member(row[0], row[0])).user

    return await bot.send_message(
        event.from_user.id,
        f'Username: @{user.username}\n'
        f'ID: {row[0]}\n\n'
        f'Full Name: {user.full_name}'
    )


@bot.callback_query_handler(
    func=lambda event: event.data.startswith('responseQuestion')
)
async def responseQuestion(event: CallbackQuery) -> None:
    data = (await getRow(event.data.split(' ')[1]))
    await bot.send_message(
        event.chat_instance,
        '✍️ Напишите ответ на заданный вам анонимный вопрос.\n'
        'ℹ️ Если вы передумали отвечать, вы можете воспользоваться '
        'кнопкой "Отменить", приложенной ниже.',
        reply_markup=Keys.cancelQuestionButton
    )
    return await setState(event.chat_instance, 'answer', data[0])


while True:
    try:
        _runner(bot.polling(non_stop=True))
    except BaseException as errorText:
        logger.syncLogger(
            f"Error while bot polling: {errorText}",
            "WAWILON-ANONQUESTIONS",
        )
