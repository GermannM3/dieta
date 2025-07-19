#!/usr/bin/env python3
"""
Скрипт для исправления админа в базе данных
"""

import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.init_database import engine, Base
from database.crud import get_user_by_email, create_user
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Хеширует пароль"""
    return pwd_context.hash(password)

def fix_admin():
    """Исправляет админа в базе данных"""
    print("🔧 Исправляем админа...")
    
    # Создаем сессию базы данных
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Проверяем существует ли админ
        admin_email = "admin@dieta.ru"
        existing_admin = get_user_by_email(db, admin_email)
        
        if existing_admin:
            print(f"❌ Админ уже существует: {existing_admin.email}")
            # Удаляем старого админа
            db.delete(existing_admin)
            db.commit()
            print("🗑️ Старый админ удален")
        
        # Создаем нового админа
        admin_data = {
            "email": admin_email,
            "hashed_password": hash_password("admin123"),
            "is_active": True,
            "is_admin": True,
            "full_name": "Администратор"
        }
        
        new_admin = create_user(db, admin_data)
        db.commit()
        
        print(f"✅ Новый админ создан: {new_admin.email}")
        print("🔑 Логин: admin@dieta.ru")
        print("🔑 Пароль: admin123")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin() 