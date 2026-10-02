from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.database.models import UserRole


class UserCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(character.isupper() for character in value):
            raise ValueError("Password must include an uppercase letter")
        if not any(character.islower() for character in value):
            raise ValueError("Password must include a lowercase letter")
        if not any(character.isdigit() for character in value):
            raise ValueError("Password must include a number")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class GoogleLoginRequest(BaseModel):
    id_token: str = Field(min_length=20, max_length=4096)


class UserRead(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead