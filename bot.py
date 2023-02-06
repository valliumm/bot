import datetime

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import apiclient.discovery


bot = Bot(token="6104534691:AAGhCIFMir8KonzQFZTvymKTeJCLbizmQDA")
dp = Dispatcher(bot)

CREDENTIALS_FILE = 'cred.json'
SRPEADSHEED_ID = '19STdLYWFHwGuf_l17ToKlp2SM4qmPW44H2vJEN54L6A'

credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                  'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http = httpAuth)


async def start(message: types.Message):
    await bot.send_message(message.from_user.id, """Вітаємо! Тут ви можете поставити анонімне запитання молодіжному пастору та служителям церкви Джерело Життя.""")

async def question(message: types.Message):
    values = [message.text, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")]
    request = service.spreadsheets().values().append(
        spreadsheetId=SRPEADSHEED_ID,
        range='A1',
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={
            'values': [values]
        }
    ).execute()
    await bot.send_message(message.from_user.id, """Дякуємо, ваше повідомлення збережене!""")



dp.register_message_handler(start, commands=['start', 'help'])
dp.register_message_handler(question)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
