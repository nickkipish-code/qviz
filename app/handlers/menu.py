from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select
from ..db import async_session
from ..models import Menu, Button
from ..keyboards.public import build_main_menu

router = Router()

@router.message(F.text)
async def handle_menu_button(msg: Message):
    # Найти кнопку по label
    async with async_session() as session:
        menu = (await session.execute(select(Menu).where(Menu.name == "Main"))).scalar_one()
        button = (await session.execute(
            select(Button).where(Button.menu_id == menu.id, Button.label == msg.text, Button.is_active == True)
        )).scalar_one_or_none()

    if not button:
        kb = await build_main_menu()
        await msg.answer("Главное меню:", reply_markup=kb)
        return

    # Простейший action: send_text
    if button.action_type == "send_text":
        await msg.answer(button.action_payload or "...")
    else:
        await msg.answer(f"Действие '{button.action_type}' пока не поддержано.")
