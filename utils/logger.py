#!/usr/bin/env python3
"""
Улучшенная система логирования с контекстом
"""
import logging
import sys
import os
from datetime import datetime
from contextlib import contextmanager
from typing import Dict, Any, Optional

# Настройка базового логирования
def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Настраивает систему логирования
    
    Args:
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Путь к файлу логов (опционально)
    
    Returns:
        Logger: Настроенный логгер
    """
    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Очищаем существующие обработчики
    root_logger.handlers.clear()
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Файловый обработчик (если указан)
    if log_file:
        # Создаем директорию для логов, если её нет
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger

# Контекстный логгер
class ContextLogger:
    """Логгер с поддержкой контекста"""
    
    def __init__(self, name: str, context: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(name)
        self.context = context or {}
    
    def _format_message(self, message: str) -> str:
        """Форматирует сообщение с контекстом"""
        if self.context:
            context_str = " | ".join([f"{k}={v}" for k, v in self.context.items()])
            return f"{message} [{context_str}]"
        return message
    
    def debug(self, message: str):
        self.logger.debug(self._format_message(message))
    
    def info(self, message: str):
        self.logger.info(self._format_message(message))
    
    def warning(self, message: str):
        self.logger.warning(self._format_message(message))
    
    def error(self, message: str):
        self.logger.error(self._format_message(message))
    
    def critical(self, message: str):
        self.logger.critical(self._format_message(message))
    
    def set_context(self, **kwargs):
        """Устанавливает контекст"""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Очищает контекст"""
        self.context.clear()

# Контекстный менеджер для логирования
@contextmanager
def log_context(logger: ContextLogger, context: Dict[str, Any]):
    """
    Контекстный менеджер для логирования с временным контекстом
    
    Args:
        logger: Логгер
        context: Контекст для логирования
    """
    old_context = logger.context.copy()
    logger.set_context(**context)
    
    try:
        yield logger
    finally:
        logger.context = old_context

# Специализированные логгеры
def get_bot_logger() -> ContextLogger:
    """Возвращает логгер для бота"""
    return ContextLogger("bot", {"component": "telegram_bot"})

def get_api_logger() -> ContextLogger:
    """Возвращает логгер для API"""
    return ContextLogger("api", {"component": "fastapi"})

def get_payment_logger() -> ContextLogger:
    """Возвращает логгер для платежей"""
    return ContextLogger("payment", {"component": "yookassa"})

def get_db_logger() -> ContextLogger:
    """Возвращает логгер для базы данных"""
    return ContextLogger("database", {"component": "postgresql"})

# Функция для логирования исключений
def log_exception(logger: ContextLogger, exception: Exception, context: Optional[Dict[str, Any]] = None):
    """
    Логирует исключение с контекстом
    
    Args:
        logger: Логгер
        exception: Исключение
        context: Дополнительный контекст
    """
    error_context = {
        "exception_type": type(exception).__name__,
        "exception_message": str(exception),
        **(context or {})
    }
    
    with log_context(logger, error_context):
        logger.error(f"Exception occurred: {exception}")
        logger.debug(f"Exception details: {exception.__class__.__name__}: {exception}")

# Функция для логирования производительности
@contextmanager
def log_performance(logger: ContextLogger, operation: str):
    """
    Контекстный менеджер для логирования производительности
    
    Args:
        logger: Логгер
        operation: Название операции
    """
    start_time = datetime.now()
    
    try:
        yield
    finally:
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Operation '{operation}' completed in {duration:.3f}s")

# Инициализация логирования по умолчанию
def init_default_logging():
    """Инициализирует логирование по умолчанию"""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "app.log")
    
    setup_logging(level=log_level, log_file=log_file)
    
    # Логируем информацию о системе
    logger = logging.getLogger("system")
    logger.info(f"Logging initialized with level: {log_level}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")

if __name__ == "__main__":
    # Тестирование логирования
    init_default_logging()
    
    bot_logger = get_bot_logger()
    api_logger = get_api_logger()
    payment_logger = get_payment_logger()
    
    bot_logger.info("Bot logger test")
    api_logger.info("API logger test")
    payment_logger.info("Payment logger test")
    
    with log_context(bot_logger, {"user_id": 123, "action": "test"}):
        bot_logger.info("Context test message")
    
    try:
        raise ValueError("Test exception")
    except Exception as e:
        log_exception(bot_logger, e, {"test": True})
    
    with log_performance(api_logger, "test_operation"):
        import time
        time.sleep(0.1) 