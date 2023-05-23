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


bot = Bot(token="6104534691:AAE2C2fo_a_wylPGiCgKNdYATSFKbh3tmN0")
dp = Dispatcher(bot, storage=MemoryStorage())

CREDENTIALS_FILE = 'cred.json'
SRPEADSHEED_ID = '19STdLYWFHwGuf_l17ToKlp2SM4qmPW44H2vJEN54L6A'

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                  'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)


kb_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
kb_start.row(KeyboardButton("Запитати ще"))


class Form(StatesGroup):
    option = State()
    contact = State()
    question = State()


start_message = """🙌🏻Привіт!

    ⁉️Тут можеш поставити питання, на яке ми з радістю дамо відповідь найближчим часом!"""

async def start(message: types.Message):
    await Form.question.set()

    await bot.send_message(message.from_user.id, start_message, reply_markup=ReplyKeyboardRemove())



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
    await bot.send_message(message.from_user.id, """💪🏼Цінуємо за довіру!""", reply_markup=kb_start)
    await state.finish()



dp.register_message_handler(start, lambda msg: msg.text.lower() in ['start', 'help', "почати з початку", "запитати ще"], state='*')
dp.register_message_handler(question, state=Form.question)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
