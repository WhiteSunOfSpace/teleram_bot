import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from flagaccess import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_TODO = {}

# Create a keyboard with predefined messages
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Introduction")],
        [KeyboardButton(text="Github link")],
        [KeyboardButton(text="Use TODO")],
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

@dp.message(F.text.contains('Github link'))
async def get_link(message: types.Message):
    link = "https://github.com/WhiteSunOfSpace"
    await message.answer(link)

@dp.message(F.text.contains('Help'))
async def cmd_help(message: types.Message):
    await message.answer('If you need help, contact us via whitesunofspace@mail.ru')

@dp.message(F.text.contains('Use TODO'))
async def cmd_act(message: types.Message):
    await message.answer('send me what you want to plan')

@dp.message()
async def check_message(message: types.Message):
    if message.text == "Introduction":
        await cmd_hello(message)
    elif message.text == "Github link":
        await cmd_hello(message)
    elif message.text == "Help":
        await cmd_hello(message)
    elif message.text == "Use TODO":
        await cmd_hello(message)
    else:
        await message.answer("Please, choose the provided options")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

