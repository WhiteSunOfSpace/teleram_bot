import aiosqlite

DB_PATH = "todo.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS todos (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                task TEXT
                            )''')
        await db.commit()


async def add_task(user_id: int, task: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO todos (user_id, task) VALUES (?, ?)", (user_id, task))
        await db.commit()


async def get_tasks(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id, task FROM todos WHERE user_id = ?", (user_id,))
        tasks = await cursor.fetchall()
        return tasks


async def delete_task(task_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM todos WHERE id = ? AND user_id = ?", (task_id, user_id))
        await db.commit()


async def clear_tasks(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM todos WHERE user_id = ?", (user_id,))
        await db.commit()
