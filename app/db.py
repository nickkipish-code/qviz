from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, func
from .config import DB_URL
from .models import Base, Rule, Menu, Button

engine = create_async_engine(DB_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Ensure default Rule and Menu
    async with async_session() as session:
        rule = (await session.execute(select(Rule).where(Rule.id == 1))).scalar_one_or_none()
        if rule is None:
            session.add(Rule(id=1, text="✅ Прочтите правила и подтвердите согласие."))
        main_menu = (await session.execute(select(Menu).where(Menu.name == "Main"))).scalar_one_or_none()
        if main_menu is None:
            main_menu = Menu(name="Main", is_active=True)
            session.add(main_menu)
            await session.flush()
            # Добавим пару демо-кнопок
            session.add_all([
                Button(menu_id=main_menu.id, label="О нас", row=1, order=0, col_span=1, is_active=True, action_type="send_text", action_payload="Мы — демо-бот 👋"),
                Button(menu_id=main_menu.id, label="Помощь", row=2, order=0, col_span=1, is_active=True, action_type="send_text", action_payload="Напишите /admin если вы админ, или /start чтобы перерисовать меню."),
            ])
        await session.commit()

async def next_order_for_row(session, menu_id: int, row: int) -> int:
    q = await session.execute(
        select(func.max(Button.order)).where(Button.menu_id == menu_id, Button.row == row)
    )
    m = q.scalar()
    return 0 if m is None else int(m) + 1
