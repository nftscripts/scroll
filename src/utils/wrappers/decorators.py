from functools import wraps
from asyncio import sleep

from typing import (
    Callable,
    Optional,
    Any,
)

from loguru import logger

from src.utils.errors.exceptions import ErrorHandler
from src.utils.gas_checker import wait_gas

from config import (
    PAUSE_BETWEEN_RETRIES,
    CHECK_GWEI,
    RETRIES,
)


def check_gas(func) -> Callable:
    def wrapper(*args, **kwargs) -> Callable:
        if CHECK_GWEI:
            wait_gas()
        return func(*args, **kwargs)

    return wrapper


def retry(retries: int = RETRIES, delay: int = PAUSE_BETWEEN_RETRIES, backoff: float = 1.5) -> Callable:
    def decorator_retry(func: Callable) -> Callable:
        @wraps(func)
        async def wrapped(*args: Optional[Any], **kwargs) -> Optional[Callable]:
            for i in range(retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as ex:
                    if i == retries:
                        logger.error(ErrorHandler(ex, *args).handle())
                    else:
                        await sleep(delay * (backoff ** i))

        return wrapped

    return decorator_retry
