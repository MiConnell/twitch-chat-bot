from __future__ import annotations

import aiosqlite

from bot.config import Config
from bot.data import command
from bot.data import esc
from bot.data import format_msg
from bot.message import Message


async def ensure_today_table_exists(db: aiosqlite.Connection) -> None:
    await db.execute(
        'CREATE TABLE IF NOT EXISTS today ('
        '   msg TEXT NOT NULL,'
        '   timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        ')',
    )
    await db.commit()


async def set_today(db: aiosqlite.Connection, msg: str) -> None:
    await ensure_today_table_exists(db)
    await db.execute('INSERT INTO today (msg) VALUES (?)', (msg,))
    await db.commit()


async def get_today(db: aiosqlite.Connection) -> str:
    await ensure_today_table_exists(db)
    query = 'SELECT msg FROM today ORDER BY ROWID DESC LIMIT 1'
    async with db.execute(query) as cursor:
        row = await cursor.fetchone()
        return 'not working on anything?' if row is None else esc(row[0])


@command('!today', '!project')
async def cmd_today(config: Config, msg: Message) -> str:
    async with aiosqlite.connect('db.db') as db:
        return format_msg(msg, await get_today(db))


@command('!settoday', secret=True)
async def cmd_settoday(config: Config, msg: Message) -> str:
    if not msg.is_moderator and msg.name_key != config.channel:
        return format_msg(msg, 'https://youtu.be/RfiQYRn7fBg')
    _, _, rest = msg.msg.partition(' ')

    async with aiosqlite.connect('db.db') as db:
        await set_today(db, rest)

    return format_msg(msg, 'updated!')
