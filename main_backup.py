from aiogram import Dispatcher
import asyncio
import logging
import sys
import time
from datetime import datetime

from core.init_bot import bot
from components.handlers.user_handlers import router as user_router
from components.handlers.admin_handlers import admin_router
from components.handlers.fat_tracker_handlers import router as fat_tracker_router
from components.payment_system.payment_handlers import router as payment_router
from database.init_database import init_db


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('bot_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class BotKeepAlive:
    def __init__(self):
        self.last_activity = time.time()
        self.restart_count = 0
        self.max_restarts = 10
        
    async def heartbeat(self):
        """Heartbeat для поддержания активности бота"""
        while True:
            try:
                # Отправляем ping каждые 30 секунд
                await bot.get_me()
                self.last_activity = time.time()
                logging.debug("Heartbeat: бот активен")
                await asyncio.sleep(30)
            except Exception as e:
                logging.warning(f"Heartbeat ошибка: {e}")
                await asyncio.sleep(10)
                
    async def activity_monitor(self):
        """Мониторинг активности бота"""
        while True:
            try:
                current_time = time.time()
                if current_time - self.last_activity > 300:  # 5 минут без активности
                    logging.warning("Бот неактивен более 5 минут, проверяем соединение...")
                    try:
                        await bot.get_me()
                        self.last_activity = current_time
                        logging.info("Соединение восстановлено")
                    except Exception as e:
                        logging.error(f"Не удалось восстановить соединение: {e}")
                        raise e
                        
                await asyncio.sleep(60)  # Проверяем каждую минуту
            except Exception as e:
                logging.error(f"Ошибка в мониторе активности: {e}")
                await asyncio.sleep(30)

async def start_polling_with_retry(dp, keep_alive):
    """Запуск polling с автоматическими повторными попытками"""
    while keep_alive.restart_count < keep_alive.max_restarts:
        try:
            logging.info(f"Запуск polling (попытка {keep_alive.restart_count + 1})")
            
            # Обновляем активность
            keep_alive.last_activity = time.time()
            
            await dp.start_polling(
                bot,
                polling_timeout=60,          # Увеличиваем таймаут
                request_timeout=30,          # Таймаут запроса
                skip_updates=False,          # Не пропускаем обновления
                allowed_updates=["message", "callback_query", "inline_query"],
                drop_pending_updates=False,  # Не удаляем pending обновления
                handle_signals=False         # Обрабатываем сигналы сами
            )
            
        except asyncio.CancelledError:
            logging.info("Polling отменен")
            break
        except Exception as e:
            keep_alive.restart_count += 1
            error_msg = f"Ошибка в polling (попытка {keep_alive.restart_count}): {e}"
            logging.error(error_msg)
            
            # Прогрессивная задержка
            delay = min(30, 5 * keep_alive.restart_count)
            logging.info(f"Перезапуск через {delay} секунд...")
            await asyncio.sleep(delay)
            
            # Попытка переподключения
            try:
                await bot.delete_webhook(drop_pending_updates=True)
                await asyncio.sleep(2)
            except:
                pass
    
    if keep_alive.restart_count >= keep_alive.max_restarts:
        logging.error("Превышено максимальное количество попыток перезапуска")
        raise RuntimeError("Критическая ошибка: бот не может поддерживать соединение")

async def main():
    """Главная функция с полной инициализацией"""
    logging.info("=" * 50)
    logging.info("🤖 Запуск Диетолог-бота")
    logging.info("=" * 50)
    
    try:
        # Инициализация базы данных
        logging.info("📊 Инициализация базы данных...")
        await init_db()
        logging.info("✅ База данных готова")
        
        # Создание диспетчера
        dp = Dispatcher()
        dp.include_routers(admin_router, payment_router, fat_tracker_router, user_router)
        logging.info("✅ Роутеры подключены")
        
        # Проверка подключения к боту
        logging.info("🔗 Проверка подключения к Telegram...")
        bot_info = await bot.get_me()
        logging.info(f"✅ Подключен как @{bot_info.username} ({bot_info.full_name})")
        
        # Очистка webhook
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("✅ Webhook очищен")
        
        # Создание системы keep-alive
        keep_alive = BotKeepAlive()
        
        # Запуск фоновых задач
        heartbeat_task = asyncio.create_task(keep_alive.heartbeat())
        monitor_task = asyncio.create_task(keep_alive.activity_monitor())
        
        logging.info("🚀 Бот запущен и готов к работе!")
        logging.info("💡 Система keep-alive активирована")
        logging.info("-" * 50)
        
        # Основной polling
        polling_task = asyncio.create_task(start_polling_with_retry(dp, keep_alive))
        
        # Ждем завершения любой из задач
        done, pending = await asyncio.wait(
            [polling_task, heartbeat_task, monitor_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Отменяем оставшиеся задачи
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
                
        # Проверяем результат
        for task in done:
            if task.exception():
                raise task.exception()
                
    except KeyboardInterrupt:
        logging.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logging.error(f"💥 Критическая ошибка: {e}")
        raise
    finally:
        try:
            await bot.session.close()
            logging.info("🔌 Соединение закрыто")
        except:
            pass

if __name__ == '__main__':
    try:
        # Установка политики событий для Windows
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("👋 Завершение работы...")
    except Exception as e:
        logging.error(f"💥 Фатальная ошибка: {e}")
        sys.exit(1)
