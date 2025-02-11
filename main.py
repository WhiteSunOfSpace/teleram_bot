import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from flagaccess import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

TODO = []

# Create a keyboard with predefined messages
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Introduction")],
        [KeyboardButton(text="Github link")],
        [KeyboardButton(text="Help")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello, this bot is ready to use:", reply_markup=keyboard)

@dp.message(F.text.contains('Introduction'))
async def cmd_hello(message: types.Message):
    await message.answer('This is bot that i use as TODO')

@dp.message(F.text.contains('link'))
async def get_link(message: types.Message):
    link = "https://github.com/WhiteSunOfSpace"
    await message.answer(link)

@dp.message(F.text.contains('Help'))
async def cmd_help(message: types.Message):
    await message.answer('If you need help, contact us via whitesunofspace@mail.ru')

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

