
from typing import Any


def resx(status: int, message: str, data : Any):
    return {"status": status, "message":message, "data": data}
