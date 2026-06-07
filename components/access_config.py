"""Бесплатный доступ и владелец бота (из .env)."""
import os
from functools import lru_cache


def _parse_id_list(raw: str | None) -> frozenset[int]:
    if not raw:
        return frozenset()
    ids: set[int] = set()
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            ids.add(int(part))
    return frozenset(ids)


@lru_cache(maxsize=1)
def get_free_user_ids() -> frozenset[int]:
    return _parse_id_list(os.getenv("FREE_USER_IDS"))


def get_owner_id() -> int | None:
    raw = os.getenv("OWNER_ID") or os.getenv("ADMIN_ID")
    return int(raw) if raw and raw.isdigit() else None


def is_free_user(user_id: int) -> bool:
    owner = get_owner_id()
    if owner is not None and user_id == owner:
        return True
    return user_id in get_free_user_ids()


def is_owner(user_id: int) -> bool:
    owner = get_owner_id()
    return owner is not None and user_id == owner
