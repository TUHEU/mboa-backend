from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token
from app.database.database import get_db
from app.database.models import User
from app.schemas.user import (
    AuthResponse,
    GoogleLoginRequest,
    LoginRequest,
    UserCreate,
)
from app.services.auth_service import (
    DuplicateEmailError,
    GoogleConfigurationError,
    GoogleTokenError,
    authenticate_user,
    get_or_create_google_user,
    register_user,
    verify_google_identity_token,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


def _auth_response(user: User) -> AuthResponse:
    return AuthResponse(
        access_token=create_access_token(user.id),
        user=user,
    )


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> AuthResponse:
    try:
        user = register_user(db, payload)
    except DuplicateEmailError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account already uses this email.",
        ) from error
    return _auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _auth_response(user)


@router.post("/google", response_model=AuthResponse)
def google_login(
    payload: GoogleLoginRequest,
    db: Session = Depends(get_db),
) -> AuthResponse:
    try:
        identity = verify_google_identity_token(
            payload.id_token,
            get_settings().google_client_id,
        )
    except GoogleConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Sign-In is not configured.",
        ) from error
    except GoogleTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google identity token is invalid or expired.",
        ) from error
    return _auth_response(get_or_create_google_user(db, identity))