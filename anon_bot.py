from aiogram import types, Dispatcher, Bot, executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

token = "5391154786:AAEwey2Gcr4EnWev8oEyqOSbNOVmpTPz0tE"
admin_id = "2132310485"
storage = MemoryStorage()

bot = Bot(token=token)

dp = Dispatcher(bot, storage=storage)

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
    executor.start_polling(dp, skip_updates=True)