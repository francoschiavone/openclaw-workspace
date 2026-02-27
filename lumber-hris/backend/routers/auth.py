"""
Authentication Router — JWT login, token validation, role checking
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.models.database import get_db, User

auth_router = APIRouter()

SECRET_KEY = "lumber-hris-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ---- Request / Response models ----

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    employee_id: Optional[str] = None
    is_active: bool = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# ---- Helper functions ----

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate user from JWT token."""
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise cred_exc
    except JWTError:
        raise cred_exc

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise cred_exc
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")
    return user


def require_role(*roles: str):
    """Dependency: check user has one of the specified roles."""
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {', '.join(roles)}"
            )
        return current_user
    return checker


# ---- Endpoints ----

@auth_router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account deactivated")

    token = create_access_token(data={
        "sub": user.email,
        "role": user.role,
        "user_id": user.id,
    })
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=user.id, email=user.email, role=user.role,
            employee_id=user.employee_id, is_active=user.is_active,
        ),
    )


@auth_router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh the access token."""
    token = create_access_token(data={
        "sub": current_user.email,
        "role": current_user.role,
        "user_id": current_user.id,
    })
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            id=current_user.id, email=current_user.email,
            role=current_user.role, employee_id=current_user.employee_id,
            is_active=current_user.is_active,
        ),
    )


@auth_router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return UserResponse(
        id=current_user.id, email=current_user.email,
        role=current_user.role, employee_id=current_user.employee_id,
        is_active=current_user.is_active,
    )
