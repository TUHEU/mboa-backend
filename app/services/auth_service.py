from dataclasses import dataclass
from secrets import token_urlsafe

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.database.models import User, UserRole
from app.schemas.user import UserCreate


class DuplicateEmailError(Exception):
    pass


class GoogleConfigurationError(Exception):
    pass


class GoogleTokenError(Exception):
    pass


@dataclass(frozen=True)
class GoogleIdentity:
    subject: str
    email: str
    full_name: str


def get_user_by_email(db: Session, email: str) -> User | None:
    normalized_email = email.strip().lower()
    return db.scalar(select(User).where(User.email == normalized_email))


def register_user(db: Session, payload: UserCreate) -> User:
    if get_user_by_email(db, payload.email) is not None:
        raise DuplicateEmailError
    user = User(
        full_name=payload.full_name.strip(),
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
        role=UserRole.tourist,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise DuplicateEmailError from error
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None or not user.is_active:
        return None
    return user if verify_password(password, user.hashed_password) else None


def verify_google_identity_token(token: str, audience: str) -> GoogleIdentity:
    if not audience:
        raise GoogleConfigurationError
    try:
        claims = google_id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            audience=audience,
        )
    except ValueError as error:
        raise GoogleTokenError from error

    email = claims.get("email")
    subject = claims.get("sub")
    if claims.get("email_verified") is not True or not isinstance(email, str):
        raise GoogleTokenError
    if not isinstance(subject, str):
        raise GoogleTokenError
    full_name = claims.get("name")
    if not isinstance(full_name, str) or len(full_name.strip()) < 2:
        full_name = email.split("@", maxsplit=1)[0]
    return GoogleIdentity(
        subject=subject,
        email=email.lower(),
        full_name=full_name.strip(),
    )


def get_or_create_google_user(db: Session, identity: GoogleIdentity) -> User:
    existing_user = get_user_by_email(db, identity.email)
    if existing_user is not None:
        return existing_user

    user = User(
        full_name=identity.full_name,
        email=identity.email,
        hashed_password=hash_password(token_urlsafe(48)),
        role=UserRole.tourist,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        linked_user = get_user_by_email(db, identity.email)
        if linked_user is None:
            raise
        return linked_user
    db.refresh(user)
    return user