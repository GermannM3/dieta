import redis
import time


r = redis.Redis()

_premium_db = {}

def check_premium(tg_id: int):
    expire = _premium_db.get(tg_id)
    return expire and expire > time.time()

def add_premium(tg_id: int, time_sec=30*24*60*60):
    _premium_db[tg_id] = int(time.time()) + time_sec


