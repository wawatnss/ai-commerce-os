"""Authentication router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.schemas import (
    EmailVerification,
    PasswordChange,
    PasswordResetConfirm,
    PasswordResetRequest,
    StoreHistoryItem,
    Token,
    UserCreate,
    UserLogin,
    UserOut,
    UserUpdate,
)
from app.auth.service import (
    authenticate_user,
    create_access_token,
    create_user,
    generate_password_reset_token,
    generate_verification_token,
    get_password_hash,
    get_user_by_email,
    verify_password,
)
from app.email import EmailService
from app.store_builder.repositories.store_repository import StoreRepository
from database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


def _send_or_log(email: str, send_fn) -> bool:
    """Send an email; never let email failure break the API."""
    try:
        return send_fn()
    except Exception:
        return False


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_email(db, data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = create_user(db, data)
    token = create_access_token({"sub": user.email})

    # Async fire-and-forget emails; failures are logged, not raised
    email_svc = EmailService()
    _send_or_log(user.email, lambda: email_svc.send_welcome(user.email))
    _send_or_log(user.email, lambda: email_svc.send_verification(user.email, generate_verification_token(user)))

    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, data)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(current_user: User = Depends(get_current_user)):
    # JWT is stateless: client must delete token. Server-side logout is a future Redis blocklist.
    return {"message": "Logout successful"}


@router.post("/password-reset-request")
def password_reset_request(data: PasswordResetRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, data.email)
    if not user:
        # Do not reveal whether email exists.
        return {"message": "If the email exists, a reset link has been sent"}
    token = generate_password_reset_token(user)
    email_svc = EmailService()
    _send_or_log(user.email, lambda: email_svc.send_password_reset(user.email, token))
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/password-reset-confirm")
def password_reset_confirm(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    from app.auth.service import decode_token

    payload = decode_token(data.token)
    if not payload or payload.get("type") != "reset" or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    user = get_user_by_email(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password updated"}


@router.post("/send-verification")
def send_verification(current_user: User = Depends(get_current_user)):
    email_svc = EmailService()
    token = generate_verification_token(current_user)
    _send_or_log(current_user.email, lambda: email_svc.send_verification(current_user.email, token))
    return {"message": "Verification email sent if configured"}


@router.post("/verify-email")
def verify_email(data: EmailVerification, db: Session = Depends(get_db)):
    from app.auth.service import decode_token

    payload = decode_token(data.token)
    if not payload or payload.get("type") != "verify" or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    user = get_user_by_email(db, payload["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
    user.email_verified = True
    db.commit()
    return {"message": "Email verified"}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(data: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.email:
        existing = get_user_by_email(db, data.email)
        if existing and existing.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        current_user.email = data.email.lower()
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/password", status_code=status.HTTP_200_OK)
def change_password(data: PasswordChange, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")
    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password changed"}


@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Delete associated stores first (or set user_id = NULL depending on policy)
    store_repo = StoreRepository(db)
    stores, _ = store_repo.list_stores_by_user(current_user.id)
    for s in stores:
        db.delete(s)
    db.delete(current_user)
    db.commit()
    return {"message": "Account and associated stores deleted"}


@router.get("/me/stores", response_model=list[StoreHistoryItem])
def my_stores(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stores, _ = StoreRepository(db).list_stores_by_user(current_user.id)
    return [
        StoreHistoryItem(
            id=s.id,
            store_name=s.store_name,
            validation_score=s.validation_score,
            created_at=s.created_at.isoformat() if s.created_at else "",
        )
        for s in stores
    ]
