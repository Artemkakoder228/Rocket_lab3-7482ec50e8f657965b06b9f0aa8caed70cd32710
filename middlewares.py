from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from cachetools import TTLCache

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 1.0):
        # Кеш, який зберігає до 10000 юзерів і автоматично очищає їх через rate_limit секунд
        self.cache = TTLCache(maxsize=10000, ttl=rate_limit)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Визначаємо ID користувача залежно від типу апдейту (повідомлення чи кнопка)
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id:
            if user_id in self.cache:
                # Якщо юзер спамить - ігноруємо обробку (можна додати await event.answer("Не спамте!"))
                return
            else:
                # Додаємо юзера в кеш
                self.cache[user_id] = True

        return await handler(event, data)