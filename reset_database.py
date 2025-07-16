import asyncio
import os
from dotenv import load_dotenv
from database.init_database import init_db, engine

load_dotenv()

async def reset_database():
    """Пересоздает базу данных с правильной структурой"""
    print("🗄️ Пересоздание базы данных...")
    
    try:
        # Удаляем все таблицы и создаем заново
        async with engine.begin() as conn:
            await conn.run_sync(lambda sync_conn: sync_conn.execute("DROP SCHEMA public CASCADE"))
            await conn.run_sync(lambda sync_conn: sync_conn.execute("CREATE SCHEMA public"))
            await conn.run_sync(lambda sync_conn: sync_conn.execute("GRANT ALL ON SCHEMA public TO postgres"))
            await conn.run_sync(lambda sync_conn: sync_conn.execute("GRANT ALL ON SCHEMA public TO public"))
        
        # Создаем новые таблицы
        await init_db()
        print("✅ База данных успешно пересоздана!")
        
    except Exception as e:
        print(f"❌ Ошибка при пересоздании БД: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(reset_database()) 