import datetime
from dataclasses import dataclass
import httplib2

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from oauth2client.service_account import ServiceAccountCredentials
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.triggers.interval import IntervalTrigger
import apiclient.discovery


bot = Bot(token="6104534691:AAGhCIFMir8KonzQFZTvymKTeJCLbizmQDA")
dp = Dispatcher(bot, storage=MemoryStorage())

CREDENTIALS_FILE = 'cred.json'
SRPEADSHEED_ID = '19STdLYWFHwGuf_l17ToKlp2SM4qmPW44H2vJEN54L6A'

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                  'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)

@dataclass
class Option:
    notanon = "Неанонімне питання"
    post = "Пост в інстаграмі/телеграмі"
    bot = "Через бота"

kb_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_start.row(KeyboardButton("На початок"))

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_client.row(KeyboardButton(Option.post), KeyboardButton(Option.bot), KeyboardButton(Option.notanon))


class Form(StatesGroup):
    option = State()
    contact = State()
    question = State()

start_message = """🙌🏻Привіт!

    ⁉️Тут можеш поставити питання, на яке ми з радістю дамо відповідь найближчим часом!
    Вкажіть, як саме ви хочете отримати відповідь? 

    - пост в інстаграмі / телеграмі
    Відповідь на кілька питань у спільному чаті Dyouth та на платформі інстаграму (наголошуємо, що автори питань завжди анонімні) 

    - через бота Dyouth

    - неаноміне питання 
    (тобто ви можете залишити контакт і ми відповімо особисто на ваше питання)"""

start_message = """🙌🏻Привіт!

    ⁉️Тут можеш поставити питання, на яке ми з радістю дамо відповідь найближчим часом!"""

async def start(message: types.Message):
    await Form.question.set()

    await bot.send_message(message.from_user.id, start_message)

async def cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await Form.question.set()
    await bot.send_message(message.from_user.id, start_message)

# async def option(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['option'] = message.text

#         if message.text == Option.bot:
#             data['id'] = message.from_user.id
#             await bot.send_message(message.from_user.id, "Чекаємо твоє питання)", reply_markup=kb_start)
#             await Form.next()
#             await Form.next()

#         if message.text == Option.post:
#             await bot.send_message(message.from_user.id, "Чекаємо твоє питання)", reply_markup=kb_start)
#             await Form.next()
#             await Form.next()

#         if message.text == Option.notanon:
#             await bot.send_message(message.from_user.id, "Будь ласка, надайте свої контакти.", reply_markup=kb_start)
#             await Form.next()

# async def contact(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['contact'] = message.text
#     await bot.send_message(message.from_user.id, "Чекаємо твоє питання)", reply_markup=kb_start)
#     await Form.next()


async def question(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['question'] = message.text
        values = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), 'Пост в інстаграмі/телеграмі', 
        data.get('contact'), data.get('id'), data.get('question'), "", "no"]
    request = service.spreadsheets().values().append(
        spreadsheetId=SRPEADSHEED_ID,
        range='A1',
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={
            'values': [values]
        }
    ).execute()
    await bot.send_message(message.from_user.id, """💪🏼Цінуємо за довіру!""")
    await state.finish()



dp.register_message_handler(cancel, lambda msg: msg.text.lower() == 'на початок', state="*")
dp.register_message_handler(start, commands=['start', 'help', "Почати з початку"])
# dp.register_message_handler(option, state=Form.option)
# dp.register_message_handler(contact, state=Form.contact)
dp.register_message_handler(question, state=Form.question)


# scheduler = AsyncIOScheduler()
# @scheduler.scheduled_job(IntervalTrigger(seconds=10))
# async def send_answer():
#     request = service.spreadsheets().values().get(spreadsheetId=SRPEADSHEED_ID, range='A1:G1000000')
#     response = request.execute()
#     for row, data in enumerate(response['values'], start=1):
#         if str(data[6]).lower() == 'no':
#             if data[5].startswith("[") and data[5].endswith("]"):
#                 await bot.send_message(data[3], data[5][1:-1])
#                 request = service.spreadsheets().values().update(
#                     spreadsheetId=SRPEADSHEED_ID,
#                     range=f'G${row}',
#                     valueInputOption='RAW',
#                     body={"values": [["yes"]]}
#                     ).execute()


if __name__ == '__main__':
    # scheduler.start()
    executor.start_polling(dp, skip_updates=True)
