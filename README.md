# Chufistov Decorators

В этом репозитории реализованы 3 различных Python-декоратора.

## validate_types

Декоратор проверяет, что аргументы функции соответствуют type_hints. 
В случае несоответствия типов данных декоратор поднимает ошибку TypeError

Пример использования:
```
from chufistov_decorators_georgechuff import validate_types

@validate_types
def add(a: int, b: int) -> int:
    return a + b

add(1, 3) -> 4
add("a", "b") -> TypeError
```

## deprecated

Декоратор, помечающий функцию как устаревшую.
При вызове выдаёт DeprecationWarning с указанным сообщением.

Пример использования:
```
@deprecated(message="Используйте new_func вместо old_func", removal_version="2.0")
def old_func() -> None:
    ...
```

## throttle
Декоратор ограничения частоты вызовов.
Если функция вызывается чаще чем раз в `rate` секунд, блокирует (sleep) до истечения интервала.

Пример использования:
```
@throttle(rate=1.0)
def api_call() -> dict:
    ...
```
