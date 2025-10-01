from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ..keyboards.public import build_main_menu
from ..db import async_session
from ..models import User, Rule
from sqlalchemy import select
import datetime
from aiogram import F

router = Router()

@router.message(Command("start"))
async def cmd_start(msg: Message):
    # Save/update user in DB
    async with async_session() as session:
        res = await session.execute(select(User).where(User.tg_id == msg.from_user.id))
        user = res.scalar_one_or_none()
        if user is None:
            user = User(
                tg_id=msg.from_user.id,
                username=msg.from_user.username,
                first_name=msg.from_user.first_name,
                last_name=msg.from_user.last_name,
                joined_at=datetime.datetime.utcnow()
            )
            session.add(user)
            await session.commit()
            # New user -> show rules
            rule_res = await session.execute(select(Rule).where(Rule.id == 1))
            rule = rule_res.scalar_one()
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Согласен", callback_data="rules:accept")]
            ])
            await msg.answer(f"{rule.text}\n\nНажмите «Согласен», чтобы открыть меню.", reply_markup=kb)
            return

    # Existing user -> show main menu
    kb = await build_main_menu()
    await msg.answer("Главное меню:", reply_markup=kb)

@router.callback_query(F.data == "rules:accept")
async def rules_accept(cb):
    kb = await build_main_menu()
    await cb.message.answer("Главное меню:", reply_markup=kb)
    await cb.answer()
