from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class UserRole(str, Enum):
    tourist = "tourist"
    business = "business"
    guide = "guide"
    administrator = "administrator"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    full_name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole, native_enum=False), default=UserRole.tourist
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )