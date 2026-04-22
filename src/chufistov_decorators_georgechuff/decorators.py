from __future__ import annotations

import functools
import inspect
import time
import warnings
from collections.abc import Callable
from typing import Any, TypeVar, get_type_hints

F = TypeVar("F", bound=Callable[..., Any])


def validate_types(func: F) -> F:
    """Декоратор, проверяющий типы аргументов и возвращаемого значения по аннотациям.

    Если аргумент или возвращаемое значение не соответствует аннотации,
    выбрасывает TypeError с понятным сообщением.
    Параметры без аннотаций не проверяются.

    Пример:

        @validate_types
        def add(a: int, b: int) -> int:
            return a + b

        add(1, 2)       # OK -> 3
        add(1, "two")   # TypeError
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        type_hints = get_type_hints(func)

        bound_args = inspect.signature(func).bind(*args, **kwargs)
        bound_args.apply_defaults()

        for param_name, param_type in bound_args.arguments.items():
            if param_name in type_hints:
                expected_type = type_hints[param_name]
                if not isinstance(param_type, expected_type):
                    raise TypeError(
                        f"Argument '{param_name}' must be {expected_type.__name__}, "
                        f"got {type(param_type).__name__}"
                    )

        result = func(*args, **kwargs)

        if "return" in type_hints:
            expected_return_type = type_hints["return"]
            if not isinstance(result, expected_return_type):
                raise TypeError(
                    f"Return value must be {expected_return_type.__name__}, "
                    f"got {type(result).__name__}"
                )

        return result

    return wrapper


def deprecated(*, message: str = "", removal_version: str | None = None) -> Callable[[F], F]:
    """Декоратор, помечающий функцию как устаревшую.

    При вызове выдаёт DeprecationWarning с указанным сообщением.

    Пример::

        @deprecated(message="Используйте new_func вместо old_func", removal_version="2.0")
        def old_func() -> None:
            ...

    Args:
        message: Текст предупреждения.
        removal_version: Версия, в которой функция будет удалена (добавляется в предупреждение).

    Returns:
        Декоратор, помечающий функцию как устаревшую.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warn_message = f"{func.__name__} is deprecated."
            if message:
                warn_message += f" {message}"
            if removal_version:
                warn_message += f" It will be removed in version {removal_version}."

            warnings.warn(warn_message, category=DeprecationWarning)
            return func(*args, **kwargs)

        return wrapper

    return decorator



def throttle(*, rate: float) -> Callable[[F], F]:
    """Декоратор ограничения частоты вызовов.

    Если функция вызывается чаще чем раз в `rate` секунд,
    блокирует (sleep) до истечения интервала.

    Пример::

        @throttle(rate=1.0)
        def api_call() -> dict:
            ...

    Args:
        rate: Минимальный интервал между вызовами в секундах.

    Returns:
        Декоратор ограничения частоты вызовов
    """

    def decorator(func: F) -> F:
        last_called = 0.0

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal last_called
            now = time.time()
            delay = now - last_called
            if delay < rate:
                time.sleep(rate - delay)
            result = func(*args, **kwargs)
            last_called = time.time()
            return result

        return wrapper

    return decorator
