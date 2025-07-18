#!/usr/bin/env python3
"""
Создание администратора для веб-приложения (синхронная версия)
"""

import os
import psycopg2
import hashlib
import secrets
from dotenv import load_dotenv

load_dotenv()

def hash_password(password):
    """Хеширование пароля"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${hash_obj.hex()}"

def create_admin_user():
    """Создание администратора"""
    
    # Получаем параметры подключения
    PGHOST = os.getenv('PGHOST')
    PGUSER = os.getenv('PGUSER')
    PGPASSWORD = os.getenv('PGPASSWORD')
    PGDATABASE = os.getenv('PGDATABASE')
    
    if not all([PGHOST, PGUSER, PGPASSWORD, PGDATABASE]):
        print("❌ Не все параметры подключения найдены в .env!")
        return False
    
    print("🔧 Создание администратора...")
    
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(
            host=PGHOST,
            user=PGUSER,
            password=PGPASSWORD,
            database=PGDATABASE,
            sslmode='require'
        )
        cur = conn.cursor()
        
        print("✅ Подключение к базе данных установлено")
        
        # Проверяем, существует ли уже администратор
        cur.execute("SELECT id, email FROM web_users WHERE email = %s", ('germannm@vk.com',))
        existing_admin = cur.fetchone()
        
        if existing_admin:
            admin_id = existing_admin[0]
            print("✅ Администратор уже существует")
            
            # Проверяем профиль
            cur.execute("SELECT id FROM web_profiles WHERE user_id = %s", (admin_id,))
            profile = cur.fetchone()
            
            if not profile:
                print("📝 Создаем профиль для администратора...")
                cur.execute("""
                    INSERT INTO web_profiles (user_id, name, is_premium, score, streak_days)
                    VALUES (%s, %s, %s, %s, %s)
                """, (admin_id, "Администратор", True, 1000, 365))
                conn.commit()
                print("✅ Профиль администратора создан")
            else:
                print("✅ Профиль администратора уже существует")
            
            cur.close()
            conn.close()
            return True
        
        # Создаем нового администратора
        print("📝 Создаем нового администратора...")
        
        # Хешируем пароль
        password_hash = hash_password("Germ@nnM3")
        
        # Создаем пользователя
        cur.execute("""
            INSERT INTO web_users (email, password_hash, name, is_confirmed)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, ('germannm@vk.com', password_hash, 'Администратор', True))
        
        admin_id = cur.fetchone()[0]
        
        # Создаем профиль
        cur.execute("""
            INSERT INTO web_profiles (user_id, name, is_premium, score, streak_days)
            VALUES (%s, %s, %s, %s, %s)
        """, (admin_id, "Администратор", True, 1000, 365))
        
        conn.commit()
        
        print("✅ Администратор создан успешно!")
        print(f"📧 Email: germannm@vk.com")
        print(f"🔑 Пароль: Germ@nnM3")
        print(f"👤 ID: {admin_id}")
        print(f"💎 Премиум: активирован")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания администратора: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("👑 Настройка администратора веб-приложения")
    print("=" * 50)
    
    success = create_admin_user()
    
    if success:
        print("\n🎉 Администратор готов!")
        print("✅ Можете войти в веб-приложение")
        print("✅ Админ-панель будет доступна после входа")
    else:
        print("\n❌ Ошибка создания администратора")

if __name__ == "__main__":
    main() 