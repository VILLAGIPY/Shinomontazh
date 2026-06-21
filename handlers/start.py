"""Bot-specific user-facing handlers.

This is what you customize — `/start`, your features, etc.
The admin panel lives in `admin_panel/` and stays untouched.
"""

import random

from aiogram import Bot, F, Router, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from core.db import add_user, user_exists
from utils.helpers import FUN_FACTS, check_channel_membership, send_channel_join_button

router = Router(name="user")


def _start_keyboard():
    builder = ReplyKeyboardBuilder()
    # Добавляем кнопки
    #builder.button(text="🛠 Услуги и цены")  потом доработать !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    builder.button(text="💬 Написать мне")
    builder.button(text="💬 Записаться")
    # Группируем их: первые две в ряд, третья ниже
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)


@router.message(CommandStart())
async def start_command(message: types.Message, bot: Bot) -> None:
    user = message.from_user
    if not await user_exists(user.id):
        await add_user(user.id, user.full_name, user.username)

    if not await check_channel_membership(bot, user.id):
        await send_channel_join_button(message, bot)
        return

    await message.answer(
        "Привет! Срочно нужен шиномонтаж, балансировка или хранение резины? 🚀\n\n"
        "Я твой личный бот-помощник: подберу удобное время и запишу за 1 минуту."
        "Жми кнопку «Записаться» ниже и приезжай без очередей!👇",
        reply_markup=_start_keyboard(),
    )


@router.message(F.text == "🛠 Услуги и цены")
async def services_handler(message: types.Message, bot: Bot) -> None:
    # Оставляем твою проверку на подписку, если она тебе нужна
    if not await check_channel_membership(bot, message.from_user.id):
        await send_channel_join_button(message, bot)
        return

    await message.answer(
        "**Мои услуги:**\n\n"
        "1. **Боты для записи (от 8 000 ₽)**\n"
        "   Идеально для шиномонтажа, моек и салонов.\n\n"
        "2. **Парсеры данных (от 3 000 ₽)**\n"
        "   Сбор инфо с Авито/WB прямо в Excel.\n\n"
        "3. **Боты-визитки (от 4 000 ₽)**\n"
        "   Авто-ответы и презентация вашего бизнеса.\n\n"
        "🚀 Срок: 2-5 дней. Поддержка включена!"
    )

@router.message(F.text == "💬 Написать мне")
async def contact_handler(message: types.Message):
    await message.answer(
        "Пиши мне напрямую: @refffiuy ✍️\n"
        "Обсудим проблемы, которые могли у вас возникнуть"
    )

@router.message(F.text == "📂 Портфолио")
async def portfolio_handler(message: types.Message):
    await message.answer(
        "Пока пусто :( \n"
        "Но скоро он заполниться вашими ботами)"
    )

