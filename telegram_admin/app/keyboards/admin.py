from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_root_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="adm:users")],
        [InlineKeyboardButton(text="📜 Правила", callback_data="adm:rules")],
        [InlineKeyboardButton(text="🧱 Главное меню", callback_data="adm:menu")],
        [InlineKeyboardButton(text="🛠 Системное", callback_data="adm:sys")],
    ])

def menu_list_kb(buttons: list[tuple[int, str, int, int, bool]]):
    """
    buttons: list of tuples (id, label, row, col_span, is_active)
    """
    rows = []
    for bid, label, row, col, active in buttons:
        status = "✅" if active else "🚫"
        rows.append([InlineKeyboardButton(text=f"{status} [{row}|{col}] {label}", callback_data=f"btn:{bid}:open")])
    rows.append([InlineKeyboardButton(text="➕ Добавить кнопку", callback_data="btn:add")])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="adm:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def button_edit_kb(button_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Текст", callback_data=f"btn:{button_id}:edit_label"),
         InlineKeyboardButton(text="↕ Ряд (1/2)", callback_data=f"btn:{button_id}:edit_row")],
        [InlineKeyboardButton(text="⇔ Ширина (1/2)", callback_data=f"btn:{button_id}:edit_colspan"),
         InlineKeyboardButton(text="👁 Вкл/Выкл", callback_data=f"btn:{button_id}:toggle")],
        [InlineKeyboardButton(text="⬆️ Вверх", callback_data=f"btn:{button_id}:up"),
         InlineKeyboardButton(text="⬇️ Вниз", callback_data=f"btn:{button_id}:down")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"btn:{button_id}:del")],
        [InlineKeyboardButton(text="⬅️ К списку", callback_data="adm:menu")]
    ])
