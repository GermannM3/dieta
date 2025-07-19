from fastapi import HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.init_database import async_session, WebUser, WebProfile
from api.email_service import email_service
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional

# JWT настройки
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Pydantic модели для API
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserConfirm(BaseModel):
    email: EmailStr
    confirmation_code: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    is_confirmed: bool
    created_at: datetime

class AuthResponse(BaseModel):
    user: UserResponse
    token: str
    message: str

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширование пароля"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Проверка пароля"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def create_token(user_id: int, email: str) -> str:
        """Создание JWT токена"""
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """Декодирование JWT токена"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Токен истек")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Неверный токен")

async def get_current_user(token: str) -> WebUser:
    """Получение текущего пользователя по токену"""
    payload = AuthService.decode_token(token)
    user_id = payload.get('user_id')
    
    async with async_session() as session:
        result = await session.execute(
            select(WebUser).where(WebUser.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=401, detail="Пользователь не найден")
        
        return user

async def register_user(user_data: UserRegister) -> AuthResponse:
    """Регистрация нового пользователя"""
    async with async_session() as session:
        # Проверяем, есть ли уже такой email
        result = await session.execute(
            select(WebUser).where(WebUser.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
        
        # Хешируем пароль
        password_hash = AuthService.hash_password(user_data.password)
        
        # Генерируем код подтверждения
        confirmation_code = email_service.generate_confirmation_code()
        
        # Создаем пользователя (автоматически подтвержденного)
        new_user = WebUser(
            email=user_data.email,
            password_hash=password_hash,
            name=user_data.name,
            confirmation_code=None,
            is_confirmed=True  # Автоматически подтверждаем
        )
        
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        # Создаем токен сразу (автоматическое подтверждение)
        token = AuthService.create_token(new_user.id, new_user.email)
        
        return AuthResponse(
            user=UserResponse(
                id=new_user.id,
                email=new_user.email,
                name=new_user.name,
                is_confirmed=new_user.is_confirmed,
                created_at=new_user.created_at
            ),
            token=token,
            message="Регистрация завершена успешно!"
        )

async def confirm_user(confirmation_data: UserConfirm) -> AuthResponse:
    """Подтверждение регистрации пользователя"""
    async with async_session() as session:
        result = await session.execute(
            select(WebUser).where(
                WebUser.email == confirmation_data.email,
                WebUser.confirmation_code == confirmation_data.confirmation_code
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=400, detail="Неверный код подтверждения")
        
        if user.is_confirmed:
            raise HTTPException(status_code=400, detail="Аккаунт уже подтвержден")
        
        # Подтверждаем пользователя
        user.is_confirmed = True
        user.confirmation_code = None
        await session.commit()
        
        # Создаем токен
        token = AuthService.create_token(user.id, user.email)
        
        return AuthResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                is_confirmed=user.is_confirmed,
                created_at=user.created_at
            ),
            token=token,
            message="Email подтвержден! Добро пожаловать!"
        )

async def login_user(login_data: UserLogin) -> AuthResponse:
    """Вход пользователя"""
    async with async_session() as session:
        result = await session.execute(
            select(WebUser).where(WebUser.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=401, detail="Неверный email или пароль")
        
        if not AuthService.verify_password(login_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Неверный email или пароль")
        
        if not user.is_confirmed:
            raise HTTPException(status_code=401, detail="Email не подтвержден. Проверьте почту.")
        
        # Создаем токен
        token = AuthService.create_token(user.id, user.email)
        
        return AuthResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                is_confirmed=user.is_confirmed,
                created_at=user.created_at
            ),
            token=token,
            message="Успешный вход!"
        ) 