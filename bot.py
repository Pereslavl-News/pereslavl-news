import asyncio
import logging
import os
from datetime import datetime, timezone
from random import choice
from typing import Literal, cast

import aiosqlite
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()

DB_NAME = os.getenv("VOTES_DB", "votes.db")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

DILEMMAS: dict[int, tuple[str, str]] = {
    1: ("Быть богатым, но одиноким", "Быть бедным, но с друзьями"),
    2: ("Уметь летать", "Читать мысли"),
    3: ("Жить 500 лет", "Жить 50 лет, но идеально"),
    4: ("Всегда говорить правду", "Всегда врать"),
    5: ("Быть супер умным", "Быть супер сильным"),
}

Choice = Literal["A", "B"]

bot = Bot(token=TOKEN) if TOKEN else None
dp = Dispatcher()


async def init_db() -> None:
    """Create the SQLite table used for vote statistics."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                dilemma_id INTEGER NOT NULL,
                choice TEXT NOT NULL CHECK(choice IN ('A', 'B')),
                created_at TEXT NOT NULL
            )
            """
        )
        await db.commit()


def main_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🎲 Дать дилемму", callback_data="get_dilemma")
    return kb.as_markup()


def dilemma_kb(dilemma_id: int, option_a: str, option_b: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=f"🅰️ {option_a}", callback_data=f"vote:{dilemma_id}:A")
    kb.button(text=f"🅱️ {option_b}", callback_data=f"vote:{dilemma_id}:B")
    kb.adjust(1)
    return kb.as_markup()


def next_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🎲 Ещё дилемму", callback_data="get_dilemma")
    return kb.as_markup()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "Привет! Я бот дилемм 🤖\nНажми кнопку и выбери сторону!",
        reply_markup=main_kb(),
    )


@dp.callback_query(F.data == "get_dilemma")
async def get_dilemma(call: CallbackQuery) -> None:
    dilemma_id = choice(list(DILEMMAS.keys()))
    option_a, option_b = DILEMMAS[dilemma_id]

    text = f"🤔 Что бы ты выбрал?\n\n🅰️ {option_a}\n🅱️ {option_b}"

    if call.message:
        await call.message.edit_text(
            text,
            reply_markup=dilemma_kb(dilemma_id, option_a, option_b),
        )
    await call.answer()


async def save_vote(user_id: int, dilemma_id: int, vote_choice: Choice) -> tuple[int, int]:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO votes (user_id, dilemma_id, choice, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                dilemma_id,
                vote_choice,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        await db.commit()

        cursor = await db.execute(
            """
            SELECT choice, COUNT(*)
            FROM votes
            WHERE dilemma_id = ?
            GROUP BY choice
            """,
            (dilemma_id,),
        )
        rows = await cursor.fetchall()

    stats = {row[0]: row[1] for row in rows}
    return stats.get("A", 0), stats.get("B", 0)


def format_results(option_a: str, option_b: str, a_count: int, b_count: int) -> str:
    total = a_count + b_count
    a_percent = round(a_count / total * 100) if total else 0
    b_percent = 100 - a_percent if total else 0

    return (
        "📊 Результаты:\n\n"
        f"🅰️ {option_a}: {a_percent}% ({a_count})\n"
        f"🅱️ {option_b}: {b_percent}% ({b_count})\n\n"
        "🔥 Продолжай играть!"
    )


@dp.callback_query(F.data.startswith("vote:"))
async def vote(call: CallbackQuery) -> None:
    try:
        _, dilemma_id_raw, vote_choice = (call.data or "").split(":")
        dilemma_id = int(dilemma_id_raw)
        if vote_choice not in {"A", "B"} or dilemma_id not in DILEMMAS:
            raise ValueError
    except ValueError:
        await call.answer("Не удалось распознать голос. Попробуй ещё раз.", show_alert=True)
        return

    option_a, option_b = DILEMMAS[dilemma_id]
    selected_choice = cast(Choice, vote_choice)
    a_count, b_count = await save_vote(call.from_user.id, dilemma_id, selected_choice)

    if call.message:
        await call.message.answer(
            format_results(option_a, option_b, a_count, b_count),
            reply_markup=next_kb(),
        )
    await call.answer("Голос засчитан!")


async def main() -> None:
    if bot is None:
        raise RuntimeError(
            "Не найден TELEGRAM_BOT_TOKEN. Создай бота через @BotFather и "
            "запусти так: TELEGRAM_BOT_TOKEN=твой_токен python bot.py"
        )

    logging.basicConfig(level=logging.INFO)
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
