from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.tickets import AdminWatchTickets, TicketAction

from admin_panel import texts as T


# ============================================================
# reply keyboards (menu navigation — persistent at chat bottom)
# ============================================================

def _kb(rows: list[list[str]]) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    sizes: list[int] = []
    for row in rows:
        for label in row:
            builder.button(text=label)
        sizes.append(len(row))
    builder.adjust(*sizes)
    return builder.as_markup(resize_keyboard=True)


def main_menu() -> ReplyKeyboardMarkup:
    return _kb([
        [T.BTN_STATS, T.BTN_BROADCAST],
        [T.BTN_USERS, T.BTN_SETTINGS],
        [T.BTN_TICKETS, T.BTN_ARCHIVE],
        [T.BTN_EXIT],
    ])


def cancel_kb() -> ReplyKeyboardMarkup:
    return _kb([[T.BTN_CANCEL]])


def users_menu() -> ReplyKeyboardMarkup:
    return _kb([
        [T.BTN_USER_FIND],
        [T.BTN_USER_BAN, T.BTN_USER_UNBAN],
        [T.BTN_BACK],
    ])


def settings_menu() -> ReplyKeyboardMarkup:
    return _kb([
        [T.BTN_ADMINS, T.BTN_CHANNELS],
        [T.BTN_MAINTENANCE, T.BTN_ACTION_LOG],
        [T.BTN_BACKUP, T.BTN_CLEAR_USERS],
        [T.BTN_BACK],
    ])


def admins_menu() -> ReplyKeyboardMarkup:
    return _kb([
        [T.BTN_ADD_ADMIN, T.BTN_REMOVE_ADMIN],
        [T.BTN_BACK],
    ])


def channels_menu() -> ReplyKeyboardMarkup:
    return _kb([
        [T.BTN_ADD_CHANNEL, T.BTN_REMOVE_CHANNEL],
        [T.BTN_BACK],
    ])


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


# ============================================================
# inline keyboards (action on a specific message)
# ============================================================

def stats_inline() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=T.BTN_INLINE_REFRESH, callback_data="admin:stats:refresh")
    b.button(text=T.BTN_INLINE_CLOSE, callback_data="admin:close")
    b.adjust(2)
    return b.as_markup()


def maintenance_inline(currently_on: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    label = T.BTN_MAINT_TURN_OFF if currently_on else T.BTN_MAINT_TURN_ON
    b.button(text=label, callback_data="admin:maint:toggle")
    b.button(text=T.BTN_INLINE_CLOSE, callback_data="admin:close")
    b.adjust(1)
    return b.as_markup()


def clear_users_inline() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=T.BTN_INLINE_YES, callback_data="admin:clear:yes")
    b.button(text=T.BTN_INLINE_NO, callback_data="admin:close")
    return b.as_markup()


def broadcast_preview_inline() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=T.BTN_BROADCAST_SEND, callback_data="admin:bc:send")
    b.button(text=T.BTN_BROADCAST_EDIT, callback_data="admin:bc:edit")
    b.button(text=T.BTN_BROADCAST_CANCEL, callback_data="admin:bc:cancel")
    b.adjust(1, 2)
    return b.as_markup()


def broadcast_stop_inline() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=T.BTN_BROADCAST_STOP, callback_data="admin:bc:stop")
    return b.as_markup()


def user_actions_inline(tg_id: int, is_banned: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if is_banned:
        b.button(text=T.BTN_USER_UNBAN_INLINE, callback_data=f"admin:user:unban:{tg_id}")
    else:
        b.button(text=T.BTN_USER_BAN_INLINE, callback_data=f"admin:user:ban:{tg_id}")
    b.button(text=T.BTN_INLINE_CLOSE, callback_data="admin:close")
    return b.as_markup()

def generate_admin_ticket_keyboard(ticket_id: int, all_ids: list[int]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    current_index = all_ids.index(ticket_id)
    
    # 1. Ряд действий: Принять / Отклонить
    b.button(text="✅ Принять", callback_data=TicketAction(action="approve", ticket_id=ticket_id, user_id=0))
    b.button(text="❌ Отклонить", callback_data=TicketAction(action="reject", ticket_id=ticket_id, user_id=0))
    
    # 2. Ряд навигации: Назад
    if current_index > 0:
        prev_id = all_ids[current_index - 1]
        b.button(text="⬅️ Назад", callback_data=AdminWatchTickets(ticket_id=prev_id, action="prev"))
    else:
        b.button(text="❌ Первая", callback_data=AdminWatchTickets(ticket_id=ticket_id, action="ignore"))
        
    # Счетчик страниц
    b.button(text=f"{current_index + 1} / {len(all_ids)}", callback_data=AdminWatchTickets(ticket_id=ticket_id, action="ignore"))
    
    # Вперед
    if current_index < len(all_ids) - 1:
        next_id = all_ids[current_index + 1]
        b.button(text="Вперед ➡️", callback_data=AdminWatchTickets(ticket_id=next_id, action="next"))
    else:
        b.button(text="❌ Последняя", callback_data=AdminWatchTickets(ticket_id=ticket_id, action="ignore"))
        
    # Ряд 3: Кнопка удаления активного тикета
    b.button(text="🗑 Удалить без ответа", callback_data=AdminWatchTickets(ticket_id=ticket_id, action="delete"))
        
    # Задаем структуру: 2 кнопки действий, 3 кнопки навигации, 1 кнопка удаления на всю ширину
    b.adjust(2, 3, 1)
    return b.as_markup()

from aiogram.filters.callback_data import CallbackData

class AdminWatchArchive(CallbackData, prefix="watch_archive"):
    ticket_id: int
    action: str  # "next", "prev", "ignore", "delete"

def generate_admin_archive_keyboard(ticket_id: int, all_ids: list[int]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    current_index = all_ids.index(ticket_id)
    
    # Ряд 1: Кнопка удаления (добавляется первой)
    b.button(text="🗑 Удалить из архива", callback_data=AdminWatchArchive(ticket_id=ticket_id, action="delete"))
    
    # Ряд 2: Кнопки навигации (Назад / Счетчик / Вперед)
    if current_index > 0:
        prev_id = all_ids[current_index - 1]
        b.button(text="⬅️ Назад", callback_data=AdminWatchArchive(ticket_id=prev_id, action="prev"))
    else:
        b.button(text="❌ Первая", callback_data=AdminWatchArchive(ticket_id=ticket_id, action="ignore"))
        
    b.button(text=f"{current_index + 1} / {len(all_ids)}", callback_data=AdminWatchArchive(ticket_id=ticket_id, action="ignore"))
    
    if current_index < len(all_ids) - 1:
        next_id = all_ids[current_index + 1]
        b.button(text="Вперед ➡️", callback_data=AdminWatchArchive(ticket_id=next_id, action="next"))
    else:
        b.button(text="❌ Последняя", callback_data=AdminWatchArchive(ticket_id=ticket_id, action="ignore"))
        
    # СТРОГО ПРОВЕРЬТЕ ЭТУ СТРОКУ:
    b.adjust(1, 3) # 1 кнопка удаления на первый ряд, 3 кнопки навигации на второй
    
    return b.as_markup()
