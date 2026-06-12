"""Миграции колонок web-таблиц (без Alembic)."""

import logging
from sqlalchemy import text
from database.init_database import engine

logger = logging.getLogger(__name__)

WEB_PROFILE_COLUMNS = [
    ("chat_context", "JSONB"),
    ("body_fat_percent", "FLOAT"),
    ("goal_fat_percent", "FLOAT"),
    ("journey_start_at", "TIMESTAMP"),
    ("conscious_streak", "INTEGER DEFAULT 0"),
    ("longest_streak", "INTEGER DEFAULT 0"),
    ("total_conscious_days", "INTEGER DEFAULT 0"),
    ("last_streak_date", "VARCHAR(10)"),
    ("starting_weight", "FLOAT"),
    ("water_date", "VARCHAR(10)"),
]

WEB_FAT_TRACKING_DDL = """
CREATE TABLE IF NOT EXISTS web_fat_tracking (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES web_users(id),
    waist_cm FLOAT NOT NULL,
    hip_cm FLOAT NOT NULL,
    neck_cm FLOAT,
    gender VARCHAR(10) NOT NULL,
    body_fat_percent FLOAT NOT NULL,
    goal_fat_percent FLOAT,
    date VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
"""


async def run_web_migrations():
    async with engine.begin() as conn:
        for col, col_type in WEB_PROFILE_COLUMNS:
            try:
                await conn.execute(text(
                    f"ALTER TABLE web_profiles ADD COLUMN IF NOT EXISTS {col} {col_type}"
                ))
            except Exception as e:
                logger.warning(f"Migration web_profiles.{col}: {e}")
        try:
            await conn.execute(text(WEB_FAT_TRACKING_DDL))
        except Exception as e:
            logger.warning(f"Migration web_fat_tracking: {e}")
    logger.info("Web migrations applied")
