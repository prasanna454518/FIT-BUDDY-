from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import String, Integer, Float, Text, DateTime
from datetime import datetime, timezone

from .config import settings


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    goal: Mapped[str] = mapped_column(String(50), nullable=False)
    intensity: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    original_plan: Mapped[str] = mapped_column(Text, nullable=False)
    updated_plan: Mapped[str | None] = mapped_column(Text, nullable=True)
    nutrition_tip: Mapped[str] = mapped_column(Text, nullable=False)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def save_user(data: dict) -> User:
    with SessionLocal() as db:
        user = User(**data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


def get_user(user_id: str) -> User | None:
    with SessionLocal() as db:
        return db.scalar(select(User).where(User.user_id == user_id))


def get_all_users() -> list[User]:
    with SessionLocal() as db:
        return list(db.scalars(select(User).order_by(User.created_at.desc())).all())


def save_plan(user_id: str, original_plan: str, nutrition_tip: str) -> Plan:
    with SessionLocal() as db:
        plan = Plan(
            user_id=user_id,
            original_plan=original_plan,
            nutrition_tip=nutrition_tip,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan


def get_plan(user_id: str) -> Plan | None:
    with SessionLocal() as db:
        return db.scalar(
            select(Plan).where(Plan.user_id == user_id).order_by(Plan.created_at.desc())
        )


def update_plan(user_id: str, updated_plan: str, feedback: str, nutrition_tip: str) -> Plan | None:
    with SessionLocal() as db:
        plan = db.scalar(
            select(Plan).where(Plan.user_id == user_id).order_by(Plan.created_at.desc())
        )
        if not plan:
            return None
        plan.updated_plan = updated_plan
        plan.feedback = feedback
        plan.nutrition_tip = nutrition_tip
        plan.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(plan)
        return plan


def delete_user(user_id: str) -> bool:
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.user_id == user_id))
        if not user:
            return False
        plans = list(db.scalars(select(Plan).where(Plan.user_id == user_id)).all())
        for plan in plans:
            db.delete(plan)
        db.delete(user)
        db.commit()
        return True
