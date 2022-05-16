from aiogram import types, Dispatcher, Bot, executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import os


BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print('You have forgot to set BOT_TOKEN')
    quit()

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv('PORT'))
token = BOT_TOKEN
admin_id = "2132310485"
storage = MemoryStorage()

bot = Bot(token=token)

dp = Dispatcher(bot, storage=storage)

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL,drop_pending_updates=True)


class States(StatesGroup):
    start = State()
    wait_for_text = State()
    
@dp.message_handler(commands=["start"], state="*")
async def start(message: types.Message):
    kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(
        text="Написать сообщение ✉", callback_data="anon"))
    await message.answer("Привет! Это бот для отправки анонимных постов в канал @advice_posts. Напишите мне о своей проблеме и она будет анонимно опубликована в канале после модерации", reply_markup=kb)


@dp.callback_query_handler(text="anon", state='*')
async def set_to_wait(call: types.CallbackQuery):
    await call.message.delete_reply_markup()
    await call.message.edit_text("Расскажи мне всё что думаешь, а я отправлю это анонимно. Пожалуйста, будь честен, пиши грамотно и не нарушай правила ❤")
    await States.wait_for_text.set()


@dp.message_handler(content_types=["text"], state=States.wait_for_text)
async def waiting(message: types.Message):
    await message.send_copy(admin_id)
    await message.answer("Большое спасибо!\nНадеюсь твою анонимную историю скоро увидят)")
    await States.start.set()


if __name__ == '__main__':
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        skip_updates=True,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
    executor.start_polling(dp, skip_updates=True)