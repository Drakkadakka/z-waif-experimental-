from typing import Callable, TypeVar, Any, Optional
import logging
import traceback
from functools import wraps
import asyncio
from utils.logging import log_error

T = TypeVar('T')

class ErrorBoundary:
    @staticmethod
    def component(fallback_value: Optional[T] = None) -> Callable:
        def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Optional[T]:
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    return func(*args, **kwargs)
                except Exception as e:
                    context = {
                        'function': func.__name__,
                        'args': str(args),
                        'kwargs': str(kwargs)
                    }
                    log_error(e, context)
                    return fallback_value
            return wrapper
        return decorator

    @staticmethod
    def system(error_handler: Optional[Callable[[Exception], Any]] = None):
        def decorator(cls: Any) -> Any:
            for attr_name, attr_value in cls.__dict__.items():
                if callable(attr_value) and not attr_name.startswith('__'):
                    wrapped = ErrorBoundary.component()(attr_value)
                    setattr(cls, attr_name, wrapped)
            return cls
        return decorator 