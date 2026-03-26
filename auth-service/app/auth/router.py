from app.auth.repository import AuthRepository
from app.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    TokenValidateRequest,
    TokenValidateResponse,
    UserResponse,
)
from app.auth.service import AuthService
from app.core.database import get_db
from app.core.security import decode_token
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer()


def get_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(AuthRepository(db))


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: RegisterRequest, svc: AuthService = Depends(get_service)):
    return await svc.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, svc: AuthService = Depends(get_service)):
    return await svc.login(data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, svc: AuthService = Depends(get_service)):
    return await svc.refresh(data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    svc: AuthService = Depends(get_service),
):
    try:
        payload = decode_token(credentials.credentials)
        user_id = payload["sub"]
    except (JWTError, KeyError):
        from fastapi import HTTPException, status

        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    return await svc.me(user_id)


# Внутренний эндпоинт для gateway — валидация токена
@router.post("/validate", response_model=TokenValidateResponse)
async def validate(data: TokenValidateRequest, svc: AuthService = Depends(get_service)):
    return await svc.validate_token(data.token)
