"""All admin-panel button labels and prompt strings in one place.

Edit these to localize or rebrand the panel.
"""

# ---- main menu ----
BTN_STATS = "📊 Статистика"
BTN_BROADCAST = "📤 Рассылка"
BTN_USERS = "👥 Пользователи"
BTN_SETTINGS = "⚙️ Настройка"
BTN_TICKETS = "🎫 Активные тикеты"
BTN_ARCHIVE = "🗄 Архив тикетов"
BTN_EXIT = "🚪 Выход из админ панели"

# ---- navigation ----
BTN_BACK = "⬅️ Назад"
BTN_CANCEL = "❌ Отмена"
BTN_REFRESH = "🔄 Обновить"
BTN_CONFIRM_YES = "✅ Yes"
BTN_CONFIRM_NO = "❌ Нет"

# ---- inline action buttons ----
BTN_INLINE_REFRESH = "🔄 Обновить"
BTN_INLINE_CLOSE = "✖️ Закрыть"
BTN_INLINE_YES = "✅ Да"
BTN_INLINE_NO = "❌ Отмена"
BTN_MAINT_TURN_ON = "🟢 Включить"
BTN_MAINT_TURN_OFF = "🔴 Выключить"
BTN_BROADCAST_SEND = "✅ Отправить всем"
BTN_BROADCAST_EDIT = "✏️ Изменить"
BTN_BROADCAST_CANCEL = "❌ Отмена"
BTN_BROADCAST_STOP = "🛑 Стоп"
BTN_USER_BAN_INLINE = "🚫 Заблокировать"
BTN_USER_UNBAN_INLINE = "✅ Разблокировать"

# ---- users ----
BTN_USER_FIND = "🔍 Найти пользователя"
BTN_USER_BAN = "🚫 Заблокировать пользователя"
BTN_USER_UNBAN = "✅ Разблокировать пользователя"

# ---- settings ----
BTN_ADMINS = "👑 Админы"
BTN_CHANNELS = "📢 Необходимые каналы"
BTN_MAINTENANCE = "🔧 Режим обслуживания"
BTN_BACKUP = "💾 Скачать базу данных"
BTN_CLEAR_USERS = "🗑 Очистить пользователей"
BTN_ACTION_LOG = "📜 Журнал действий"

BTN_ADD_ADMIN = "➕ Добавить админа"
BTN_REMOVE_ADMIN = "➖ Удалить админа"
BTN_ADD_CHANNEL = "➕ Добавить канал"
BTN_REMOVE_CHANNEL = "➖ Удалить канал"

# ---- titles ----
TITLE_MAIN = "👑 <b>Панель администратора</b>\n\nВыберите действие:"
TITLE_STATS = "📊 <b>Статистика</b>"
TITLE_BROADCAST_PROMPT = (
    "✍️ Отправьте сообщение, которое хотите распространить.\n\n"
    "Подходят любые типы сообщений (текст, фото, видео, документы, стикеры)."
)
TITLE_BROADCAST_PREVIEW = "👆 Вот что получат пользователи. Выберите действие:"
TITLE_USERS = "👥 <b>Пользователи</b>"
TITLE_SETTINGS = "⚙️ <b>Настройки</b>"
TITLE_ADMINS = "👑 <b>Админы</b>"
TITLE_CHANNELS = "📢 <b>Необходимые каналы</b>"
TITLE_MAINTENANCE = "🔧 <b>Режим обслуживания</b>"
TITLE_ACTION_LOG = "📜 <b>Последние действия администратора</b>"

MSG_EXIT = "Панель администратора закрыта."
MSG_NOT_AUTHORIZED = "🚫 Вам не разрешено использовать эту команду."
MSG_CANCELLED = "Отменено."
MSG_MAINTENANCE_ON = (
    "🔧 В данный момент бот находится на техническом обслуживании. Пожалуйста, попробуйте позже."
)
MSG_BANNED = "🚫 Вам запрещено использовать этого бота."

MSG_USER_INFO = (
    "<b>Информация о пользователе</b>\n\n"
    "ID: <code>{id}</code>\n"
    "Имя: {name}\n"
    "Имя пользователя: {username}\n"
    "Присоединился: {joined}\n"
    "Админ: {is_admin}\n"
    "Запрещено: {is_banned}"
)
