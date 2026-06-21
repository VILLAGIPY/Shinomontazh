from aiogram import F, Router
from aiogram.types import Message, CallbackQuery


# Импортируем функции БД, клавиатуру и фабрику
from core.db import get_all_pending_ids, get_ticket_by_id
from admin_panel.keyboards import generate_admin_ticket_keyboard
from handlers.tickets import AdminWatchTickets
# Arcihe
from admin_panel.texts import BTN_TICKETS, BTN_ARCHIVE  # <-- Импортируем новую константу
from core.db import get_all_pending_ids, get_ticket_by_id, get_all_archive_ids, delete_ticket_by_id   # <-- И функцию БД
from admin_panel.keyboards import generate_admin_ticket_keyboard, generate_admin_archive_keyboard, AdminWatchArchive
# В aiogram 3.x используем локальный роутер для этого файла
router = Router()

# Хэндлер на текстовую кнопку "🎫 Активные тикеты"
@router.message(F.text == "🎫 Активные тикеты")
async def admin_start_watching(message: Message):
    pending_ids = await get_all_pending_ids()
    if not pending_ids:
        return await message.answer("⏳ Активных заявок на рассмотрении нет!")

    first_id = pending_ids[0]
    ticket = await get_ticket_by_id(first_id)
    
    text = (
        f"🎫 **Заявка на рассмотрении [{pending_ids.index(first_id) + 1}/{len(pending_ids)}]**\n\n"
        f"🚗 Марка: {ticket['car_brand']}\n"
        f"🛠 Проблема: {ticket['problem']}\n"
        f"📅 Время: {ticket['booking_time']}\n"
        f"📞 Телефон: {ticket['phone']}"
    )

    kb = generate_admin_ticket_keyboard(ticket_id=first_id, all_ids=pending_ids)
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")


# Хэндлер переключения стрелочек (CallbackQuery)
@router.callback_query(AdminWatchTickets.filter())
async def process_admin_ticket_pagination(callback: CallbackQuery, callback_data: AdminWatchTickets):
    if callback_data.action == "ignore":
        return await callback.answer()

    # ==========================================
    # ЛОГИКА УДАЛЕНИЯ АКТИВНОГО ТИКЕТА
    # ==========================================
    if callback_data.action == "delete":
        # Получаем текущий список до удаления, чтобы зафиксировать позицию админа
        old_pending_ids = await get_all_pending_ids()
        
        try:
            current_index = old_pending_ids.index(callback_data.ticket_id)
        except ValueError:
            current_index = 0

        # Удаляем запись из БД (используем ту же функцию из core/db.py)
        from core.db import delete_ticket_by_id
        await delete_ticket_by_id(callback_data.ticket_id)
        await callback.answer("Заявка успешно удалена!")
        
        # Получаем обновленный список активных тикетов
        pending_ids = await get_all_pending_ids()
        
        # Если активных тикетов больше не осталось
        if not pending_ids:
            await callback.message.edit_text("⏳ Активных заявок на рассмотрении нет!")
            return

        # Вычисляем, какую заявку показать следующей
        if current_index >= len(pending_ids):
            current_index = len(pending_ids) - 1
            
        target_id = pending_ids[current_index]

    # ==========================================
    # ЛОГИКА СТРЕЛОЧЕК (НАЗАД / ВПЕРЕД)
    # ==========================================
    else:
        pending_ids = await get_all_pending_ids()
        if not pending_ids:
            await callback.message.edit_text("⏳ Активных заявок на рассмотрении нет!")
            return await callback.answer()

        target_id = callback_data.ticket_id
        if target_id not in pending_ids:
            target_id = pending_ids

    # ==========================================
    # АВТОМАТИЧЕСКИЙ ПЕРЕРЕНДЕР ИНТЕРФЕЙСА
    # ==========================================
    ticket = await get_ticket_by_id(target_id)
    
    text = (
        f"🎫 **Заявка на рассмотрении [{pending_ids.index(target_id) + 1}/{len(pending_ids)}]**\n\n"
        f"🚗 Марка: {ticket['car_brand']}\n"
        f"🛠 Проблема: {ticket['problem']}\n"
        f"📅 Время: {ticket['booking_time']}\n"
        f"📞 Телефон: {ticket['phone']}"
    )

    kb = generate_admin_ticket_keyboard(ticket_id=target_id, all_ids=pending_ids)
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")



@router.callback_query(AdminWatchArchive.filter())
async def process_admin_archive_pagination(callback: CallbackQuery, callback_data: AdminWatchArchive):
    if callback_data.action == "ignore":
        return await callback.answer()

    # ==========================================
    # ЛОГИКА УДАЛЕНИЯ ТИКЕТА
    # ==========================================
    if callback_data.action == "delete":
        # Сначала получаем текущий список, чтобы узнать, на каком индексе стоял админ
        old_archive_ids = await get_all_archive_ids()
        
        try:
            current_index = old_archive_ids.index(callback_data.ticket_id)
        except ValueError:
            current_index = 0

        # Удаляем запись из БД
        await delete_ticket_by_id(callback_data.ticket_id)
        await callback.answer("Заявка успешно удалена из архива!")
        
        # Получаем новый список ID после удаления
        archive_ids = await get_all_archive_ids()
        
        # Если архив стал абсолютно пустым
        if not archive_ids:
            await callback.message.edit_text("🗄 Архив пуст.")
            return

        # Умное определение следующего тикета:
        # Если удалили последний тикет в списке, сдвигаем индекс назад на 1 шаг
        if current_index >= len(archive_ids):
            current_index = len(archive_ids) - 1
            
        target_id = archive_ids[current_index]
    
    # ==========================================
    # ЛОГИКА КЛИКА ПО СТРЕЛОЧКАМ (НАЗАД / ВПЕРЕД)
    # ==========================================
    else:
        archive_ids = await get_all_archive_ids()
        if not archive_ids:
            await callback.message.edit_text("🗄 Архив пуст.")
            return await callback.answer()

        target_id = callback_data.ticket_id
        # Если тикет кто-то удалил параллельно, сбрасываем на первый доступный
        if target_id not in archive_ids:
            target_id = archive_ids[0]

    # ==========================================
    # АВТОМАТИЧЕСКОЕ ОБНОВЛЕНИЕ ИНТЕРФЕЙСА
    # ==========================================
    ticket = await get_ticket_by_id(target_id)
    status_emoji = "✅ Одобрена" if ticket['status'] == "approved" else "❌ Отклонена"
    
    text = (
        f"🗄 **Архивная заявка №{target_id} [{archive_ids.index(target_id) + 1}/{len(archive_ids)}]**\n"
        f"📊 Статус: **{status_emoji}**\n\n"
        f"🚗 Марка: {ticket['car_brand']}\n"
        f"🛠 Проблема: {ticket['problem']}\n"
        f"📅 Время: {ticket['booking_time']}\n"
        f"📞 Телефон: {ticket['phone']}"
    )

    kb = generate_admin_archive_keyboard(ticket_id=target_id, all_ids=archive_ids)
    
    # Редактируем текущее сообщение без отправки нового
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

@router.message(F.text == "🗄 Архив тикетов")
async def admin_start_watching_archive(message: Message):
    archive_ids = await get_all_archive_ids()
    if not archive_ids:
        return await message.answer("🗄 Архив рассмотренных заявок пока пуст.")

    first_id = archive_ids[0] # Берем самый первый тикет в архиве
    ticket = await get_ticket_by_id(first_id)
    
    # Определяем статус для вывода
    status_emoji = "✅ Одобрена" if ticket['status'] == "approved" else "❌ Отклонена"
    
    text = (
        f"🗄 **Архивная заявка №{first_id} [1/{len(archive_ids)}]**\n"
        f"📊 Статус: **{status_emoji}**\n\n"
        f"🚗 Марка: {ticket['car_brand']}\n"
        f"🛠 Проблема: {ticket['problem']}\n"
        f"📅 Время: {ticket['booking_time']}\n"
        f"📞 Телефон: {ticket['phone']}"
    )

    kb = generate_admin_archive_keyboard(ticket_id=first_id, all_ids=archive_ids)
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")
