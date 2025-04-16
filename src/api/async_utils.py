import asyncio
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")


def to_async(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    """Convert a synchronous function to an asynchronous one using thread pools.

    This decorator allows running synchronous I/O-bound functions in a separate thread
    to avoid blocking the asyncio event loop.

    Args:
        func: The synchronous function to convert to async.

    Returns:
        An async wrapper function that runs the original function in a thread pool.
    """

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper
