from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.callback_data import CallbackData

# Импортируем функции работы с БД из вашей папки core
from core.db import add_ticket, update_ticket_status, get_ticket_by_id

# Импортируем ваш конфиг для получения ID группы админов
import config  # Убедитесь, что в config.py есть переменная GROUP_ID

router = Router()

# ==========================================
# 1. МАШИНА СОСТОЯНИЙ (FSM) ДЛЯ СБОРА ДАННЫХ
# ==========================================
class TicketStates(StatesGroup):
    car_brand = State()
    problem = State()
    booking_time = State()
    phone = State()
    
from aiogram.fsm.state import State, StatesGroup
class AdminRejectStates(StatesGroup):
    waiting_for_reason = State()
# ==========================================
# 2. ФАБРИКА КОЛБЭКОВ ДЛЯ КНОПОК АДМИНИСТРАТОРА
# ==========================================
class TicketAction(CallbackData, prefix="ticket"):
    action: str  # "approve" или "reject"
    ticket_id: int
    user_id: int


# ==========================================
# 3. ХЭНДЛЕРЫ ЗАПОЛНЕНИЯ ТИКЕТА ПОЛЬЗОВАТЕЛЕМ
# ==========================================

@router.message(F.text == "💬 Записаться")
async def start_ticket(message: Message, state: FSMContext):
    """Пользователь нажал кнопку 'Записаться'. Запускаем FSM."""
    await state.set_state(TicketStates.car_brand)
    await message.answer(
        "Введите марку и модель вашей машины:", 
        reply_markup=ReplyKeyboardRemove()  # Убираем старую клавиатуру на время заполнения
    )


@router.message(TicketStates.car_brand)
async def process_brand(message: Message, state: FSMContext):
    """Сохраняем марку машины, переходим к проблеме."""
    await state.update_data(car_brand=message.text)
    await state.set_state(TicketStates.problem)
    await message.answer("Опишите проблему или необходимую услугу:")


@router.message(TicketStates.problem)
async def process_problem(message: Message, state: FSMContext):
    """Сохраняем проблему, переходим к времени."""
    await state.update_data(problem=message.text)
    await state.set_state(TicketStates.booking_time)
    await message.answer("Укажите желаемое время и дату записи:")

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
@router.message(TicketStates.booking_time)
async def process_time(message: Message, state: FSMContext):
    """Сохраняем время, переходим к номеру телефона."""
    await state.update_data(booking_time=message.text)
    await state.set_state(TicketStates.phone)
    
    # Создаем клавиатуру с кнопкой запроса контакта
    phone_markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    # Отправляем сообщение вместе с этой кнопкой
    await message.answer("Нажмите на кнопку ниже, чтобы автоматически отправить свой номер телефона для связи:", reply_markup=phone_markup)


@router.message(TicketStates.phone)
async def process_phone(message: Message, state: FSMContext, bot: Bot):
    """Последний шаг: сохраняем в БД и отправляем заявку в группу админов."""
    user_data = await state.get_data()
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text
    await state.clear()  # Сбрасываем состояние пользователя

    # Сохраняем тикет в БД через вашу структуру core.db
    ticket_id = await add_ticket(
        user_id=message.from_user.id,
        car_brand=user_data['car_brand'],
        problem=user_data['problem'],
        booking_time=user_data['booking_time'],
        phone=phone
    )

    # Формируем inline-кнопки для группы админов
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Принять", 
                callback_data=TicketAction(action="approve", ticket_id=ticket_id, user_id=message.from_user.id).pack()
            ),
            InlineKeyboardButton(
                text="❌ Отклонить", 
                callback_data=TicketAction(action="reject", ticket_id=ticket_id, user_id=message.from_user.id).pack()
            )
        ]
    ])

    # Текст карточки заявки
    # Текст карточки заявки (переделан под безопасный HTML)
    ticket_text = (
        f"📋 <b>Новая заявка №{ticket_id}</b>\n\n"
        f"👤 Клиент: {message.from_user.full_name} (@{message.from_user.username or 'нет юзернейма'})\n"
        f"🚗 Марка: {user_data['car_brand']}\n"
        f"🛠 Проблема: {user_data['problem']}\n"
        f"📅 Время: {user_data['booking_time']}\n"
        f"📞 Телефон: {phone}"
    )

    # Отправляем сообщение в админ-чат группы (изменили parse_mode на HTML)
    await bot.send_message(
        chat_id=config.GROUP_ID, 
        text=ticket_text, 
        reply_markup=admin_kb, 
        parse_mode="HTML"
    )
    
    # Отвечаем пользователю (здесь вы можете вернуть его главное меню)
    await message.answer("Ваша заявка успешно отправлена на рассмотрение! Ожидайте ответа администратора.",reply_markup=ReplyKeyboardRemove())


# ==========================================
# 4. ОБРАБОТКА РЕШЕНИЯ АДМИНИСТРАТОРА В ГРУППЕ
# ==========================================

@router.callback_query(TicketAction.filter())
async def handle_admin_decision(callback: CallbackQuery, callback_data: TicketAction, state: FSMContext, bot: Bot):
    """Единый хэндлер, который точно поймает клик по кнопке"""
    
    # --- СЦЕНАРИЙ 1: НАЖАТА КНОПКА "ПРИНЯТЬ" ---
    if callback_data.action == "approve":
        await update_ticket_status(callback_data.ticket_id, "approved")

        # Если кликнули из админ-панели (где user_id=0), достаем реальный ID юзера из БД
        target_user_id = callback_data.user_id
        if target_user_id == 0:
            ticket = await get_ticket_by_id(callback_data.ticket_id)
            if ticket:
                target_user_id = ticket['user_id']
# Перевели текст для пользователя на HTML (вместо ** используем <b>)
        user_msg = f"Ваша заявка №{callback_data.ticket_id} была <b>одобрена</b>! Администратор свяжется с вами."

        try:
            if target_user_id != 0:
                # Изменили parse_mode на HTML
                await bot.send_message(chat_id=target_user_id, text=user_msg, parse_mode="HTML")
        except Exception:
            pass

        # Перевели текст обновления карточки на HTML (вместо ** используем <b>)
        new_text = callback.message.text + f"\n\n<b>Статус:</b> ✅ Одобрена (изменил: {callback.from_user.full_name})"
        # Изменили parse_mode на HTML
        await callback.message.edit_text(text=new_text, reply_markup=None, parse_mode="HTML")
        await callback.answer()

    # --- СЦЕНАРИЙ 2: НАЖАТА КНОПКА "ОТКЛОНИТЬ" ---
    elif callback_data.action == "reject":
        # Включаем FSM админа для ввода причины
        await state.set_state(AdminRejectStates.waiting_for_reason)
        
        # Сохраняем контекст заявки в память FSM
        await state.update_data(
            reject_ticket_id=callback_data.ticket_id,
            reject_user_id=callback_data.user_id,
            admin_message_id=callback.message.message_id,
            admin_chat_id=callback.message.chat.id,
            old_text=callback.message.text
        )
        
        await callback.message.reply(
            f"📝 Напишите причину отказа для заявки №{callback_data.ticket_id}:"
        )
        await callback.answer()

# ==========================================
# 6. ПРИЕМ ПРИЧИНЫ ОТКАЗА И ОТПРАВКА КЛИЕНТУ
# ==========================================
@router.message(AdminRejectStates.waiting_for_reason)
async def process_reject_reason(message: Message, state: FSMContext, bot: Bot):
    """Админ написал причину. Фиксируем отказ."""
    reason_text = message.text
    
    admin_data = await state.get_data()
    await state.clear()  # Сбрасываем состояние

    ticket_id = admin_data['reject_ticket_id']
    target_user_id = admin_data['reject_user_id']

    # Обновляем БД
    await update_ticket_status(ticket_id, "rejected")

    # Если кликнули из админки (user_id=0), подтягиваем реальный ID пользователя из БД
    if target_user_id == 0:
        ticket = await get_ticket_by_id(ticket_id)
        if ticket:
            target_user_id = ticket['user_id']

 # Уведомляем клиента (перевели на HTML)
    if target_user_id != 0:
        user_msg = (
            f"❌ К сожалению, ваша заявка №{ticket_id} была <b>отклонена</b>.\n\n"
            f"💬 <b>Причина отказа:</b> {reason_text}"
        )
        try:
            await bot.send_message(chat_id=target_user_id, text=user_msg, parse_mode="HTML")
        except Exception:
            pass

    # Красиво обновляем исходную карточку в группе (перевели на HTML)
    new_text = (
        f"{admin_data['old_text']}\n\n"
        f"❌ <b>Отклонена</b> (изменил: {message.from_user.full_name})\n"
        f"💬 <b>Причина:</b> {reason_text}"
    )
    
    try:
        await bot.edit_message_text(
            chat_id=admin_data['admin_chat_id'],
            message_id=admin_data['admin_message_id'],
            text=new_text,
            reply_markup=None,
            parse_mode="HTML"  # Изменили на HTML
        )
    except Exception:
        pass

    await message.answer(f"✅ Заявка №{ticket_id} отклонена. Причина отправлена клиенту.")

class AdminWatchTickets(CallbackData, prefix="watch_ticket"):
    ticket_id: int
    action: str  # "next", "prev", "ignore"
class AdminRejectStates(StatesGroup):
    waiting_for_reason = State()