from app.auth.models import User
from app.auth.repository import AuthRepository
from app.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    TokenValidateResponse,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from fastapi import HTTPException, status
from jose import JWTError


class AuthService:
    def __init__(self, repo: AuthRepository):
        self.repo = repo

    async def register(self, data: RegisterRequest) -> TokenResponse:
        if await self.repo.get_by_email(data.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
        )
        user = await self.repo.create(user)
        return self._issue_tokens(str(user.id))

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Account disabled")
        return self._issue_tokens(str(user.id))

    async def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError
        except Exception:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

        user = await self.repo.get_by_id(payload["sub"])
        if not user or not user.is_active:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
        return self._issue_tokens(str(user.id))

    async def me(self, user_id: str) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        return user

    async def validate_token(self, token: str) -> TokenValidateResponse:
        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                return TokenValidateResponse(valid=False)
            return TokenValidateResponse(
                valid=True,
                user_id=payload["sub"],
                email=payload.get("email"),
            )
        except JWTError:
            return TokenValidateResponse(valid=False)

    @staticmethod
    def _issue_tokens(user_id: str) -> TokenResponse:
        return TokenResponse(
            access_token=create_access_token(user_id),
            refresh_token=create_refresh_token(user_id),
        )
