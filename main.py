import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from flagaccess import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_TODO = {}

valid_options = ["Introduction", "Github link", "Use TODO", "Help", "/start"]

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Introduction")],
        [KeyboardButton(text="Github link")],
        [KeyboardButton(text="Use TODO")],
        [KeyboardButton(text="Help")]
    ],
    resize_keyboard=True
)

todo_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Show tasks")],
        [KeyboardButton(text="Delete task")],
        [KeyboardButton(text="Clear all")]
    ],
    resize_keyboard=True
)

class TodoState(StatesGroup):
    wait_for_input = State()

class DeleteState(StatesGroup):
    wait_for_input = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello, this bot is ready to use:", reply_markup=keyboard)

@dp.message(F.text.contains('Introduction'))
async def cmd_hello(message: types.Message, state: FSMContext):
    await message.answer('This is a bot that I use as a TODO.')
    await state.clear()

@dp.message(F.text.contains('Show task'))
async def cmd_hello(message: types.Message, state: FSMContext):
    uid = message.from_user.id
    if uid in user_TODO and user_TODO[uid]:
        todo_list = "\n".join([f"{num}) {task}" for num, task in enumerate(user_TODO[uid], start=1)])
        await message.answer(f"Your TODO is:\n{todo_list}", reply_markup=todo_keyboard)
    else:
        await message.answer('Your TODO is empty', reply_markup=keyboard)
    await state.clear()

@dp.message(F.text.contains('Github link'))
async def get_link(message: types.Message, state: FSMContext):
    await message.answer("https://github.com/WhiteSunOfSpace")
    await state.clear()

@dp.message(F.text.contains('Help'))
async def cmd_help(message: types.Message, state: FSMContext):
    await message.answer('If you need help, contact us via whitesunofspace@mail.ru')
    await state.clear()

@dp.message(F.text.contains('Delete task'))
async def cmd_delete(message: types.Message, state: FSMContext):
    await message.answer('Put the number of task which need to delete')
    await state.set_state(DeleteState.wait_for_input)

@dp.message(DeleteState.wait_for_input)
async def process_todo_delete(message: types.Message, state: FSMContext):
    num = int(message.text)
    user_id = message.from_user.id
    temp = []
    for i in range(len(user_TODO[user_id])):
        if i != num-1:
            temp.append(user_TODO[user_id][i])
    user_TODO[user_id] = temp
    await message.answer("Task is delete", reply_markup=todo_keyboard)
    await state.clear()

async def cmd_act(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in user_TODO:
        user_TODO[user_id] = []

    await message.answer('You are in TODO menu now\nSend me task and i will save it', reply_markup=todo_keyboard)
    await state.set_state(TodoState.wait_for_input)

@dp.message(TodoState.wait_for_input)
async def process_todo_input(message: types.Message, state: FSMContext):
    if message.text.lower() == "exit":
        await message.answer("You are in main menu now.", reply_markup=keyboard)
        await state.clear()
        return

    user_id = message.from_user.id
    user_TODO[user_id].append(message.text)
    await message.answer("Saved! Send another or type 'exit'.", reply_markup=todo_keyboard)

@dp.message(F.text.in_(valid_options))
async def handle_valid_message(message: types.Message, state: FSMContext):
    if message.text == "Introduction":
        await cmd_hello(message)
    elif message.text == "Github link":
        await get_link(message)
    elif message.text == "Help":
        await cmd_help(message)
    elif message.text == "Use TODO":
        await cmd_act(message, state)

@dp.message()
async def handle_invalid_message(message: types.Message):
    await message.answer("Please select an option from the menu.", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
