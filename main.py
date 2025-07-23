from aiogram import Dispatcher
import asyncio
import logging
import sys
import time
import signal
from datetime import datetime

from core.init_bot import bot
from components.handlers.user_handlers import router as user_router
from components.handlers.admin_handlers import admin_router
from components.handlers.fat_tracker_handlers import router as fat_tracker_router
from components.payment_system.payment_handlers import router as payment_router
from database.init_database import init_db
from utils.logger import init_default_logging, get_bot_logger, log_exception, log_performance


# Инициализация улучшенного логирования
init_default_logging()
logger = get_bot_logger()

class BotKeepAlive:
    def __init__(self):
        self.last_activity = time.time()
        self.restart_count = 0
        self.max_restarts = 10
        self._shutdown_event = False
        
    async def heartbeat(self):
        """Heartbeat для поддержания активности бота"""
        while not self._shutdown_event:
            try:
                # Отправляем ping каждые 30 секунд
                await bot.get_me()
                self.last_activity = time.time()
                logger.debug("Heartbeat: бот активен")
                await asyncio.sleep(30)
            except Exception as e:
                if not self._shutdown_event:
                    logger.warning(f"Heartbeat ошибка: {e}")
                    await asyncio.sleep(10)
                
    async def activity_monitor(self):
        """Мониторинг активности бота"""
        while not self._shutdown_event:
            try:
                current_time = time.time()
                if current_time - self.last_activity > 300:  # 5 минут без активности
                    logger.warning("Бот неактивен более 5 минут, проверяем соединение...")
                    try:
                        await bot.get_me()
                        self.last_activity = current_time
                        logger.info("Соединение восстановлено")
                    except Exception as e:
                        logger.error(f"Не удалось восстановить соединение: {e}")
                        raise e
                        
                await asyncio.sleep(60)  # Проверяем каждую минуту
            except Exception as e:
                if not self._shutdown_event:
                    logger.error(f"Ошибка в мониторе активности: {e}")
                    await asyncio.sleep(30)
    
    def shutdown(self):
        """Сигнал для завершения работы"""
        self._shutdown_event = True

async def start_polling_with_retry(dp, keep_alive):
    """Запуск polling с автоматическими повторными попытками"""
    while keep_alive.restart_count < keep_alive.max_restarts and not keep_alive._shutdown_event:
        try:
            logger.info(f"Запуск polling (попытка {keep_alive.restart_count + 1})")
            
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
            logger.info("Polling отменен")
            break
        except Exception as e:
            if keep_alive._shutdown_event:
                break
            keep_alive.restart_count += 1
            error_msg = f"Ошибка в polling (попытка {keep_alive.restart_count}): {e}"
            logger.error(error_msg)
            
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
        logger.error("Превышено максимальное количество попыток перезапуска")
        raise RuntimeError("Критическая ошибка: бот не может поддерживать соединение")

async def graceful_shutdown(keep_alive, tasks):
    """Graceful shutdown бота"""
    logger.info("Начинаю graceful shutdown бота...")
    
    # Сигнализируем о завершении
    keep_alive.shutdown()
    
    # Отменяем все задачи
    for task in tasks:
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    # Закрываем соединение с ботом
    try:
        await bot.session.close()
        logger.info("🔌 Соединение с ботом закрыто")
    except Exception as e:
        logger.error(f"Ошибка при закрытии соединения: {e}")

async def main():
    """Главная функция с полной инициализацией"""
    logger.info("=" * 50)
    logger.info("🤖 Запуск Диетолог-бота")
    logger.info("=" * 50)
    
    keep_alive = None
    tasks = []
    
    try:
        # Инициализация базы данных
        logger.info("📊 Инициализация базы данных...")
        await init_db()
        logger.info("✅ База данных готова")
        
        # Создание диспетчера
        dp = Dispatcher()
        dp.include_routers(admin_router, payment_router, fat_tracker_router, user_router)
        logger.info("✅ Роутеры подключены")
        
        # Проверка подключения к боту
        logger.info("🔗 Проверка подключения к Telegram...")
        bot_info = await bot.get_me()
        logger.info(f"✅ Подключен как @{bot_info.username} ({bot_info.full_name})")
        
        # Очистка webhook
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook очищен")
        
        # Создание системы keep-alive
        keep_alive = BotKeepAlive()
        
        # Запуск фоновых задач
        heartbeat_task = asyncio.create_task(keep_alive.heartbeat())
        monitor_task = asyncio.create_task(keep_alive.activity_monitor())
        tasks = [heartbeat_task, monitor_task]
        
        logger.info("🚀 Бот запущен и готов к работе!")
        logger.info("💡 Система keep-alive активирована")
        logger.info("-" * 50)
        
        # Основной polling
        polling_task = asyncio.create_task(start_polling_with_retry(dp, keep_alive))
        tasks.append(polling_task)
        
        # Ждем завершения любой из задач
        done, pending = await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Проверяем результат
        for task in done:
            if task.exception() and not isinstance(task.exception(), asyncio.CancelledError):
                raise task.exception()
                
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        raise
    finally:
        if keep_alive and tasks:
            await graceful_shutdown(keep_alive, tasks)

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    logger.info(f"Получен сигнал {signum}, начинаю graceful shutdown...")
    # Сигнал будет обработан в основном цикле через KeyboardInterrupt

if __name__ == '__main__':
    try:
        # Установка политики событий для Windows
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Регистрируем обработчики сигналов
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # На Windows также обрабатываем SIGBREAK
        if hasattr(signal, 'SIGBREAK'):
            signal.signal(signal.SIGBREAK, signal_handler)
        
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Завершение работы...")
    except Exception as e:
        logger.error(f"💥 Фатальная ошибка: {e}")
        sys.exit(1)
