from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update, delete
from ..config import ADMINS
from ..keyboards.admin import admin_root_kb, menu_list_kb, button_edit_kb
from ..db import async_session, next_order_for_row
from ..models import Menu, Button

router = Router(name="admin")

# ===== Вход =====
@router.message(Command("admin"))
async def admin_entry(msg: Message):
    if msg.from_user.id not in ADMINS:
        await msg.answer("⛔ Нет доступа в админ-панель.")
        return
    await msg.answer("Админ-панель:", reply_markup=admin_root_kb())

@router.callback_query(F.data == "adm:back")
async def adm_back(cb: CallbackQuery):
    await cb.message.edit_text("Админ-панель:", reply_markup=admin_root_kb())
    await cb.answer()

# ===== Раздел «Главное меню» =====
@router.callback_query(F.data == "adm:menu")
async def adm_menu_root(cb: CallbackQuery):
    async with async_session() as session:
        menu = (await session.execute(select(Menu).where(Menu.name == "Main"))).scalar_one()
        btns = (await session.execute(
            select(Button).where(Button.menu_id == menu.id).order_by(Button.row.asc(), Button.order.asc())
        )).scalars().all()
    payload = [(b.id, b.label, b.row, b.col_span, b.is_active) for b in btns]
    await cb.message.edit_text("🧱 Главное меню — список кнопок:", reply_markup=menu_list_kb(payload))
    await cb.answer()

# ===== Просмотр/редактирование одной кнопки =====
@router.callback_query(F.data.startswith("btn:") & F.data.endswith(":open"))
async def btn_open(cb: CallbackQuery):
    bid = int(cb.data.split(":")[1])
    async with async_session() as session:
        b = (await session.execute(select(Button).where(Button.id == bid))).scalar_one()
    txt = (f"Кнопка #{b.id}\n"
           f"Текст: {b.label}\nРяд: {b.row}\nШирина(col_span): {b.col_span}\nАктивна: {b.is_active}\n"
           f"Порядок: {b.order}\nAction: {b.action_type}\nPayload: {b.action_payload or '(пусто)'}")
    await cb.message.edit_text(txt, reply_markup=button_edit_kb(b.id))
    await cb.answer()

# ===== Добавление кнопки (FSM) =====
class AddBtn(StatesGroup):
    label = State()
    row = State()
    col = State()
    text = State()

@router.callback_query(F.data == "btn:add")
async def btn_add_start(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(AddBtn.label)
    await cb.message.edit_text("➕ Введите текст кнопки:")
    await cb.answer()

@router.message(AddBtn.label)
async def btn_add_label(msg: Message, state: FSMContext):
    await state.update_data(label=msg.text)
    await state.set_state(AddBtn.row)
    await msg.answer("Ряд кнопки? Введите `1` или `2`.")

@router.message(AddBtn.row)
async def btn_add_row(msg: Message, state: FSMContext):
    if msg.text not in ("1", "2"):
        await msg.answer("Введите 1 или 2.")
        return
    await state.update_data(row=int(msg.text))
    await state.set_state(AddBtn.col)
    await msg.answer("Ширина кнопки? Введите `1` или `2` (2 — широкая).")

@router.message(AddBtn.col)
async def btn_add_col(msg: Message, state: FSMContext):
    if msg.text not in ("1", "2"):
        await msg.answer("Введите 1 или 2.")
        return
    await state.update_data(col=int(msg.text))
    await state.set_state(AddBtn.text)
    await msg.answer("Текст сообщения при нажатии (action=send_text):")

@router.message(AddBtn.text)
async def btn_add_save(msg: Message, state: FSMContext):
    data = await state.get_data()
    label = data["label"]
    row = data["row"]
    col = data["col"]
    payload_text = msg.text

    async with async_session() as session:
        menu = (await session.execute(select(Menu).where(Menu.name == "Main"))).scalar_one()
        order = await next_order_for_row(session, menu.id, row)
        session.add(Button(
            menu_id=menu.id,
            label=label,
            row=row,
            order=order,
            col_span=col,
            is_active=True,
            action_type="send_text",
            action_payload=payload_text
        ))
        await session.commit()

    await state.clear()
    await msg.answer("✅ Кнопка добавлена.\nНажмите /admin → «🧱 Главное меню», чтобы посмотреть список.")

# ===== Редактирование полей =====
class EditLabel(StatesGroup):
    waiting = State()

@router.callback_query(F.data.startswith("btn:") & F.data.endswith(":edit_label"))
async def btn_edit_label_start(cb: CallbackQuery, state: FSMContext):
    bid = int(cb.data.split(":")[1])
    await state.set_state(EditLabel.waiting)
    await state.update_data(bid=bid)
    await cb.message.answer("✏️ Введите новый текст кнопки:")
    await cb.answer()

@router.message(EditLabel.waiting)
async def btn_edit_label_save(msg: Message, state: FSMContext):
    data = await state.get_data()
    bid = data["bid"]
    async with async_session() as session:
        await session.execute(
            update(Button).where(Button.id == bid).values(label=msg.text)
        )
        await session.commit()
    await state.clear()
    await msg.answer("✅ Текст обновлён. Откройте /admin → «🧱 Главное меню».")

@router.callback_query(F.data.startswith("btn:") & F.data.endswith(":edit_row"))
async def btn_edit_row(cb: CallbackQuery):
    bid = int(cb.data.split(":")[1])
    async with async_session() as session:
        b = (await session.execute(select(Button).where(Button.id == bid))).scalar_one()
        new_row = 2 if b.row == 1 else 1
        # поместим в конец нового ряда
        new_order = await next_order_for_row(session, b.menu_id, new_row)
        b.row = new_row
        b.order = new_order
        await session.commit()
    await cb.answer("Ряд переключён.")
    await btn_open(cb)

@router.callback_query(F.data.startswith("btn:") & F.data.endswith(":edit_colspan"))
async def btn_edit_col(cb: CallbackQuery):
    bid = int(cb.data.split(":")[1])
    async with async_session() as session:
        b = (await session.execute(select(Button).where(Button.id == bid))).scalar_one()
        b.col_span = 1 if b.col_span == 2 else 2
        await session.commit()
    await cb.answer("Ширина изменена.")
    await btn_open(cb)

@router.callback_query(F.data.startswith("btn:") & F.data.endswith(":toggle"))
async def btn_toggle(cb: CallbackQuery):
    bid = int(cb.data.split(":")[1])
    async with async_session() as session:
        b = (await session.execute(select(Button).where(Button.id == bid))).scalar_one()
        b.is_active = not b.is_active
        await session.commit()
    await cb.answer("Видимость переключена.")
    await btn_open(cb)

# ===== Порядок в ряду (up/down) =====
@router.callback_query(F.data.startswith("btn:") & F.data.endswith(":up"))
async def btn_up(cb: CallbackQuery):
    bid = int(cb.data.split(":")[1])
    async with async_session() as session:
        b = (await session.execute(select(Button).where(Button.id == bid))).scalar_one()
        if b.order == 0:
            await cb.answer("И так верхняя.")
            return
        # ищем соседа сверху
        prev = (await session.execute(
            select(Button).where(Button.menu_id == b.menu_id, Button.row == b.row, Button.order == b.order - 1)
        )).scalar_one_or_none()
        if prev:
            prev.order, b.order = b.order, prev.order
            await session.commit()
    await cb.answer("Перемещено вверх.")
    await btn_open(cb)

@router.callback_query(F.data.startswith("btn:") & F.data.endswith(":down"))
async def btn_down(cb: CallbackQuery):
    bid = int(cb.data.split(":")[1])
    async with async_session() as session:
        b = (await session.execute(select(Button).where(Button.id == bid))).scalar_one()
        # ищем соседа снизу
        nextb = (await session.execute(
            select(Button).where(Button.menu_id == b.menu_id, Button.row == b.row, Button.order == b.order + 1)
        )).scalar_one_or_none()
        if nextb:
            nextb.order, b.order = b.order, nextb.order
            await session.commit()
    await cb.answer("Перемещено вниз.")
    await btn_open(cb)

# ===== Удаление =====
@router.callback_query(F.data.startswith("btn:") & F.data.endswith(":del"))
async def btn_delete(cb: CallbackQuery):
    bid = int(cb.data.split(":")[1])
    async with async_session() as session:
        b = (await session.execute(select(Button).where(Button.id == bid))).scalar_one_or_none()
        if b:
            await session.execute(delete(Button).where(Button.id == bid))
            # сдвиг order у нижних не обязателен, можно оставить «дыры»
            await session.commit()
    await cb.answer("Удалено.")
    # Вернуться к списку
    await adm_menu_root(cb)
