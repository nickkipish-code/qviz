from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, Text, DateTime, ForeignKey
import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer, unique=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    joined_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)

class Rule(Base):
    __tablename__ = "rules"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text, default="Правила будут здесь")
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Menu(Base):
    __tablename__ = "menus"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), unique=True, default="Main")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    buttons: Mapped[list["Button"]] = relationship(back_populates="menu", cascade="all, delete-orphan", order_by="Button.order")

class Button(Base):
    __tablename__ = "buttons"
    id: Mapped[int] = mapped_column(primary_key=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menus.id"))
    label: Mapped[str] = mapped_column(String(64))
    row: Mapped[int] = mapped_column(Integer, default=1)                # 1 или 2
    order: Mapped[int] = mapped_column(Integer, default=0)              # порядок в ряду
    col_span: Mapped[int] = mapped_column(Integer, default=1)           # 1 или 2 (широкая)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    action_type: Mapped[str] = mapped_column(String(32), default="send_text")
    action_payload: Mapped[str] = mapped_column(Text, default="")       # для send_text — сам текст

    menu: Mapped["Menu"] = relationship(back_populates="buttons")
