"""Core data layer for the bot's `users` table.

Admin-panel tables (admins, banned, channels, settings, action_log) live
in `admin_panel/db.py`. Both modules share the same SQLite file via
`config.DB_PATH`.
"""

from typing import Optional

import aiosqlite

from config import DB_PATH


async def init_users_table() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.commit()

# 1. Функция инициализации таблицы (вызовется при старте бота)
async def init_tickets_table():
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                car_brand TEXT,
                problem TEXT,
                booking_time TEXT,
                phone TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)
        await db.commit()

# 2. Функция для сохранения нового тикета
async def add_ticket(user_id: int, car_brand: str, problem: str, booking_time: str, phone: str) -> int:
    async with aiosqlite.connect("bot.db") as db:
        cursor = await db.execute(
            """INSERT INTO tickets (user_id, car_brand, problem, booking_time, phone) 
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, car_brand, problem, booking_time, phone)
        )
        ticket_id = cursor.lastrowid
        await db.commit()
        return ticket_id

# 3. Функция для обновления статуса тикета (когда админ нажал кнопку)
async def update_ticket_status(ticket_id: int, status: str):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("UPDATE tickets SET status = ? WHERE id = ?", (status, ticket_id))
        await db.commit()

# 4. Функция для получения активных тикетов (для админки)
async def get_pending_tickets():
    async with aiosqlite.connect("bot.db") as db:
        async with db.execute("SELECT id, car_brand, booking_time FROM tickets WHERE status = 'pending'") as cursor:
            return await cursor.fetchall()

async def user_exists(telegram_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cur:
            return await cur.fetchone() is not None


async def add_user(telegram_id: int, name: str, username: Optional[str]) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO users (telegram_id, name, username)
            VALUES (?, ?, ?)
            """,
            (telegram_id, name, username),
        )
        await db.commit()

# Получить список всех ID тикетов со статусом 'pending'
async def get_all_pending_ids() -> list[int]:
    async with aiosqlite.connect("bot.db") as db:
        async with db.execute("SELECT id FROM tickets WHERE status = 'pending' ORDER BY id ASC") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

# Получить полные данные тикета по его ID
async def get_ticket_by_id(ticket_id: int) -> dict | None:
    async with aiosqlite.connect("bot.db") as db:
        db.row_factory = aiosqlite.Row  # Чтобы обращаться к полям по именам
        async with db.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
        
# Получить список всех ID тикетов со статусом 'approved' или 'rejected'
async def get_all_archive_ids() -> list[int]:
    async with aiosqlite.connect("bot.db") as db:
        async with db.execute(
            "SELECT id FROM tickets WHERE status IN ('approved', 'rejected') ORDER BY id DESC"
        ) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
        
async def delete_ticket_by_id(ticket_id: int):
    async with aiosqlite.connect("bot.db") as db:
        await db.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
        await db.commit()