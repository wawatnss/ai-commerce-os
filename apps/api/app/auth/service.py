"""Authentication service."""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.schemas import UserCreate, UserLogin
from config import settings


def _to_bytes(s: str) -> bytes:
    return s.encode("utf-8")


def _from_bytes(b: bytes) -> str:
    return b.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(_to_bytes(plain), _to_bytes(hashed))


def get_password_hash(password: str) -> str:
    # bcrypt has 72-byte limit; truncate safely
    pwd = _to_bytes(password)[:72]
    return _from_bytes(bcrypt.hashpw(pwd, bcrypt.gensalt()))


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email.lower()).first()


def create_user(db: Session, data: UserCreate) -> User:
    user = User(
        email=data.email.lower(),
        hashed_password=get_password_hash(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, data: UserLogin) -> Optional[User]:
    user = get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def generate_password_reset_token(user: User) -> str:
    payload = {
        "sub": user.email,
        "type": "reset",
        "jti": secrets.token_urlsafe(16),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def generate_verification_token(user: User) -> str:
    payload = {
        "sub": user.email,
        "type": "verify",
        "jti": secrets.token_urlsafe(16),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
