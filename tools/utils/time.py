import random
import time
from functools import wraps
from typing import Callable, ParamSpec, Type, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def sleep_decorator(
    min_seconds: float, max_seconds: float
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator that introduces a random sleep within the specified range of seconds.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result = func(*args, **kwargs)
            sleep_time = random.uniform(min_seconds, max_seconds)
            time.sleep(sleep_time)
            return result

        return wrapper

    return decorator


def retry(
    max_attempts: int = 3, delay: float = 0, exceptions: tuple[Type[Exception], ...] = (Exception,)
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator that retries a function a specified number of times on specific exceptions.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exception: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        if delay > 0:
                            time.sleep(delay)
                        continue
            if last_exception:
                raise last_exception
            raise Exception("Max attempts reached")

        return wrapper

    return decorator
