import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database import init_db, add_task, get_tasks, delete_task, clear_tasks
from flagaccess import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_TODO = {}

valid_options = ["Introduction", "Github link", "Use TODO", "Help"]

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
        [KeyboardButton(text="Add task")],
        [KeyboardButton(text="Show tasks")],
        [KeyboardButton(text="Delete task")],
        [KeyboardButton(text="Clear all")],
        [KeyboardButton(text="Exit")]
    ],
    resize_keyboard=True
)


class DeleteState(StatesGroup):
    wait_for_input = State()


class AddState(StatesGroup):
    wait_for_input = State()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello, this bot is ready to use:", reply_markup=keyboard)


@dp.message(F.text == 'Introduction')
async def cmd_hello(message: types.Message, state: FSMContext):
    await message.answer('This is a bot that I use as a TODO.')
    await state.clear()


@dp.message(F.text == 'Show tasks')
async def cmd_show(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    tasks = await get_tasks(user_id)

    if tasks:
        todo_list = "\n".join([f"{num}) {task[0]}" for num, task in enumerate(tasks, start=1)])
        await message.answer(f"Your TODO is:\n{todo_list}", reply_markup=todo_keyboard)
    else:
        await message.answer('Your TODO is empty', reply_markup=todo_keyboard)
    await state.clear()


@dp.message(F.text == 'Clear all')
async def cmd_clear(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    tasks = await get_tasks(user_id)

    if tasks:
        await clear_tasks(user_id)
        await message.answer('All your tasks were deleted', reply_markup=keyboard)
    else:
        await message.answer('Your TODO list is already empty', reply_markup=keyboard)
    await state.clear()


@dp.message(F.text == 'Exit')
async def cmd_ext(message: types.Message, state: FSMContext):
    await message.answer('You are in main menu', reply_markup=keyboard)
    await state.clear()


@dp.message(F.text == 'Github link')
async def get_link(message: types.Message, state: FSMContext):
    await message.answer("https://github.com/WhiteSunOfSpace")
    await state.clear()


@dp.message(F.text == 'Help')
async def cmd_help(message: types.Message, state: FSMContext):
    await message.answer('If you need help, contact us via whitesunofspace@mail.ru')
    await state.clear()


@dp.message(F.text == 'Add task')
async def cmd_add(message: types.Message, state: FSMContext):
    await message.answer('What do you want to plan?')
    await state.set_state(AddState.wait_for_input)


@dp.message(AddState.wait_for_input)
async def process_todo_add(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if message.text.strip():
        await add_task(user_id, message.text.strip())
        await message.answer('Saved!', reply_markup=todo_keyboard)
    else:
        await message.answer('The task must be a text message')

    await state.clear()


@dp.message(F.text == 'Delete task')
async def cmd_delete(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    tasks = await get_tasks(user_id)

    if tasks:
        await message.answer('Put the number of the task you want to delete:')
        await state.set_state(DeleteState.wait_for_input)
    else:
        await message.answer('Your TODO list is already empty', reply_markup=todo_keyboard)


@dp.message(DeleteState.wait_for_input)
async def process_todo_delete(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    tasks = await get_tasks(user_id)

    try:
        num = int(message.text)
        if num < 1 or num > len(tasks):
            await message.answer("Invalid task number. Please try again", reply_markup=todo_keyboard)
        else:
            task = tasks[num - 1]
            await delete_task(task)
            await message.answer("Task deleted successfully", reply_markup=todo_keyboard)
    except:
        await message.answer("Please enter a number", reply_markup=todo_keyboard)

    await state.clear()


async def cmd_act(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_TODO:
        user_TODO[user_id] = []
    await message.answer('You are in TODO menu now', reply_markup=todo_keyboard)


@dp.message(F.text.in_(valid_options))
async def handle_valid_message(message: types.Message):
    if message.text == "Introduction":
        await cmd_hello(message)
    elif message.text == "Github link":
        await get_link(message)
    elif message.text == "Help":
        await cmd_help(message)
    elif message.text == "Use TODO":
        await cmd_act(message)


@dp.message()
async def handle_invalid_message(message: types.Message):
    await message.answer("Please select an option from the menu.", reply_markup=keyboard)


async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
