import logging
import sqlite3
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import token



bot = Bot(token=token)
dp = Dispatcher()

connection = sqlite3.connect("tasks.db", check_same_thread=False)
cursor = connection.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    user_id INTEGER,
    task TEXT
)
""")
connection.commit()

@dp.message(Command('start'))
async def start(message: types.Message):
    await message.answer("Привет! Я бот для управления задачами. Используй команду /add, чтобы добавить задачу, /view — чтобы посмотреть все задачи, и /delete — чтобы удалить задачу.")

@dp.message(Command('add'))
async def add_task(message: types.Message):
    await message.answer("Введите задачу ответив на данное сообщение:")


@dp.message(Command('view'))
async def view_notes(message: types.Message):
    cursor.execute("SELECT task FROM tasks WHERE user_id = ?", (message.from_user.id,))
    tasks = cursor.fetchall()
    if tasks:
        response = '\n'.join([note[0] for note in tasks])
    else:
        response = "У вас нет задач."
    await message.answer(response)


@dp.message(Command('delete'))
async def delete(message: types.Message):
    cursor.execute("SELECT id, task FROM tasks WHERE user_id = ?", (message.from_user.id,))
    tasks = cursor.fetchall()

    if tasks:
        response = '\n'.join([f"{task[0]}. {task[1]}" for task in tasks])
        response += "\nВведите номер задачи, которую хотите удалить ответив на данное сообщение."
        await message.answer(response)
    else:
        await message.answer("У вас нет задач для удаления.")


@dp.message()
async def handle_message(message: types.Message):
    if message.reply_to_message:
        if 'Введите задачу ответив на данное сообщение' in message.reply_to_message.text:
            task_text = message.text
            cursor.execute('INSERT INTO tasks (user_id, task) VALUES (?, ?)', (message.from_user.id, task_text))
            connection.commit()
            await message.answer("Задача сохранена!")

        elif 'Введите номер задачи, которую хотите удалить ответив на данное сообщение' in message.reply_to_message.text:
            try:
                task_id = int(message.text)
                cursor.execute("SELECT id FROM tasks WHERE id = ? AND user_id = ?", (task_id, message.from_user.id))
                task = cursor.fetchone()
                if task:
                    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                    connection.commit()
                    await message.answer("Задача удалена!")
                else:
                    await message.answer("Задача с таким номером не найдена.")
            except ValueError:
                await message.answer("Пожалуйста, введите корректный номер задачи.")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")