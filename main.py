import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database import init_db, add_task, get_tasks, delete_task, clear_tasks
from flagaccess import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

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

confirmation = InlineKeyboardBuilder()
confirmation.add(InlineKeyboardButton(text="No", callback_data="opt1"))
confirmation.add(InlineKeyboardButton(text="Yes", callback_data="opt2"))


class DeleteState(StatesGroup):
    wait_for_input = State()


class AddState(StatesGroup):
    wait_for_input = State()


class ConfirmState(StatesGroup):
    wait_for_input = State()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello, this bot is ready to use:", reply_markup=keyboard)


@dp.message(F.text == 'Introduction')
async def cmd_hello(message: types.Message, state: FSMContext):
    await state.update_data(last_markup=keyboard)
    await message.answer('This is a bot that I use as a TODO.')


@dp.message(F.text == 'Show tasks')
async def cmd_show(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    tasks = await get_tasks(user_id)

    if tasks:
        todo_list = "\n".join([f"{num}) {task[1]}" for num, task in enumerate(tasks, start=1)])
        await message.answer(f"Your TODO is:\n{todo_list}", reply_markup=todo_keyboard)
    else:
        await message.answer('Your TODO is empty', reply_markup=todo_keyboard)
    await state.clear()


@dp.message(F.text == 'Clear all')
async def cmd_clear(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    tasks = await get_tasks(user_id)

    if tasks:
        await message.answer('Are you sure you want to delete all tasks?', reply_markup=confirmation.as_markup())
        await state.set_state(ConfirmState.wait_for_input)
    else:
        await message.answer('Your TODO list is already empty', reply_markup=keyboard)


@dp.callback_query(ConfirmState.wait_for_input)
async def handle_callback(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    print(user_id)
    if callback.data == "opt1":
        await callback.message.answer("Return to TODO menu", reply_markup=todo_keyboard)
    else:
        await clear_tasks(user_id)
        await callback.message.answer('All your tasks were deleted', reply_markup=keyboard)
    await callback.answer()
    await state.clear()


@dp.message(F.text == 'Exit')
async def cmd_ext(message: types.Message, state: FSMContext):
    await message.answer('You are in main menu', reply_markup=keyboard)
    await state.clear()


@dp.message(F.text == 'Github link')
async def get_link(message: types.Message, state: FSMContext):
    await state.update_data(last_markup=keyboard)
    await message.answer("https://github.com/WhiteSunOfSpace")


@dp.message(F.text == 'Help')
async def cmd_help(message: types.Message, state: FSMContext):
    await state.update_data(last_markup=keyboard)
    await message.answer('If you need help, contact us via whitesunofspace@mail.ru')


@dp.message(F.text == 'Add task')
async def cmd_add(message: types.Message, state: FSMContext):
    await message.answer('What do you want to plan?')
    await state.set_state(AddState.wait_for_input)


@dp.message(AddState.wait_for_input)
async def process_todo_add(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    try:
        msg = message.text.strip()
        await add_task(user_id, msg)
        await message.answer('Saved!', reply_markup=todo_keyboard)
    except AttributeError:
        await message.answer('The task must be a text message')

    await state.clear()


@dp.message(F.text == 'Delete task')
async def cmd_delete(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    tasks = await get_tasks(user_id)
    await state.update_data(tasks=tasks)
    if tasks:
        await message.answer('Put the number of the task you want to delete:')
        await state.set_state(DeleteState.wait_for_input)
    else:
        await message.answer('Your TODO list is already empty', reply_markup=todo_keyboard)


@dp.message(DeleteState.wait_for_input)
async def process_todo_delete(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    tasks = data.get('tasks', [])
    try:
        num = int(message.text)
        if num < 1 or num > len(tasks):
            await message.answer("Invalid task number. Please try again.", reply_markup=todo_keyboard)
        else:
            task_id = tasks[num - 1][0]
            await delete_task(task_id, user_id)
            await message.answer("Task deleted successfully.", reply_markup=todo_keyboard)
    except ValueError:
        await message.answer("Please enter a valid number.", reply_markup=todo_keyboard)
    await state.clear()


async def cmd_act(message: types.Message, state: FSMContext):
    await state.update_data(last_markup=todo_keyboard)
    await message.answer('You are in TODO menu now', reply_markup=todo_keyboard)


@dp.message(F.text.in_(valid_options))
async def handle_valid_message(message: types.Message, state: FSMContext):
    if message.text == "Introduction":
        await cmd_hello(message, state)
    elif message.text == "Github link":
        await get_link(message, state)
    elif message.text == "Help":
        await cmd_help(message, state)
    elif message.text == "Use TODO":
        await cmd_act(message, state)


@dp.message()
async def handle_invalid_message(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    last_markup = user_data.get("last_markup", keyboard)
    await message.answer("Please select an option from the menu.", reply_markup=last_markup)


async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
