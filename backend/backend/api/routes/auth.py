from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from backend.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from backend.db.session import get_db
from backend.models.user import User
from backend.schemas.user import (
    Token,
    UserCreate,
    UserOut,
)  # ✅ Corrected schema import

router = APIRouter(prefix="", tags=["auth"])


# ---------- REGISTER ----------------------------------------------------------


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account."""
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_pw = hash_password(user_in.password)
    new_user = User(username=user_in.username, hashed_password=hashed_pw)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ---------- LOGIN -------------------------------------------------------------


@router.post("/login", response_model=Token)
def login(user_in: UserCreate, db: Session = Depends(get_db)):
    """Authenticate user and return JWT bearer token."""
    user = db.query(User).filter(User.username == user_in.username).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.username})
    return Token(access_token=token)


# ---------- CURRENT USER ------------------------------------------------------


@router.get("/me", response_model=UserOut)
def me(authorization: str = Header(...), db: Session = Depends(get_db)):
    """Return the currently authenticated user (by JWT)."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Bearer token")

    token = authorization.replace("Bearer ", "")
    try:
        user = get_current_user(token, db)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
