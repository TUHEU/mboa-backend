from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.database.models import User
from app.schemas.user import UserRead


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user
