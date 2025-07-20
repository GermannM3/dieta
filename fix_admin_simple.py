#!/usr/bin/env python3
import subprocess
import sys

def fix_admin():
    print("🔧 Исправление админа germannm@vk.com через Docker...")
    
    # Получаем ID API контейнера
    try:
        result = subprocess.run(
            "docker ps -q --filter 'name=api'", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        container_id = result.stdout.strip()
        
        if not container_id:
            print("❌ API контейнер не найден!")
            return
            
        print(f"✅ Найден API контейнер: {container_id}")
        
    except Exception as e:
        print(f"❌ Ошибка поиска контейнера: {e}")
        return
    
    # Python код для выполнения в контейнере
    python_code = '''
import asyncio
import bcrypt
from database.init_database import async_session_maker
from sqlalchemy import text

async def fix_admin():
    print("🔧 Исправление админа germannm@vk.com...")
    
    password = "Germ@nnM3"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    
    async with async_session_maker() as session:
        try:
            result = await session.execute(
                text("SELECT id, email, is_admin FROM users WHERE email = :email"),
                {"email": "germannm@vk.com"}
            )
            user = result.fetchone()
            
            if user:
                print(f"✅ Пользователь найден: {user.email}")
                
                await session.execute(
                    text("""
                        UPDATE users 
                        SET password_hash = :password_hash, 
                            is_admin = true,
                            is_verified = true
                        WHERE email = :email
                    """),
                    {
                        "password_hash": hashed_password.decode("utf-8"),
                        "email": "germannm@vk.com"
                    }
                )
                print("✅ Пароль обновлен и пользователь сделан админом")
            else:
                print("❌ Пользователь не найден, создаем нового...")
                
                await session.execute(
                    text("""
                        INSERT INTO users (email, password_hash, is_admin, is_verified, created_at)
                        VALUES (:email, :password_hash, true, true, NOW())
                    """),
                    {
                        "email": "germannm@vk.com",
                        "password_hash": hashed_password.decode("utf-8")
                    }
                )
                print("✅ Новый админ создан")
            
            await session.commit()
            print("✅ Изменения сохранены в базе")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            await session.rollback()

asyncio.run(fix_admin())
'''
    
    # Выполняем код в контейнере
    try:
        cmd = f'docker exec {container_id} python3 -c "{python_code}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        print("📄 Вывод:")
        print(result.stdout)
        
        if result.stderr:
            print("❌ Ошибки:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")

if __name__ == "__main__":
    fix_admin() 