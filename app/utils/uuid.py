import uuid
from typing import Optional


def cast_uuid(uuid_str: str) -> Optional[uuid.UUID]:
    try:
        return uuid.UUID(uuid_str)
    except ValueError:
        return None
