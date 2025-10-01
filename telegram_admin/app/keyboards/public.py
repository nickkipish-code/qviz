from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy import select
from ..db import async_session
from ..models import Menu, Button

async def build_main_menu():
    async with async_session() as session:
        menu = (await session.execute(select(Menu).where(Menu.name == "Main", Menu.is_active == True))).scalar_one_or_none()
        if not menu:
            # Пустая клавиатура, чтобы не падать
            return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Меню недоступно")]])
        buttons = (await session.execute(
            select(Button).where(Button.menu_id == menu.id, Button.is_active == True).order_by(Button.row.asc(), Button.order.asc())
        )).scalars().all()

    row1, row2 = [], []
    for b in buttons:
        btn = KeyboardButton(text=b.label)
        if b.row == 1:
            if b.col_span == 2:
                row1 = [btn]  # широкая, одна в ряду
            else:
                row1.append(btn)
        else:
            if b.col_span == 2:
                row2 = [btn]
            else:
                row2.append(btn)

    keyboard = []
    if row1: keyboard.append(row1)
    if row2: keyboard.append(row2)
    if not keyboard:
        keyboard = [[KeyboardButton(text="(пусто)")]]

    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=keyboard)
