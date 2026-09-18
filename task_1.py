import random
from typing import Dict
import time
from collections import deque

class SlidingWindowRateLimiter():
    def __init__(self, window_size: int = 10, max_requests: int = 1) -> None:
        self.size = window_size
        self.max_requests = max_requests
        self.messages: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        if len(self.messages[user_id]) == 0:
            return
        oldest_message_time = self.messages[user_id][0]
        elapsed_time = current_time - oldest_message_time
        while elapsed_time > self.size:
            self.messages[user_id].popleft()
            if len(self.messages[user_id]) == 0:
                break
            oldest_message_time = self.messages[user_id][0]
            elapsed_time = current_time - oldest_message_time

    def can_send_message(self, user_id: str) -> bool:
        if user_id not in self.messages:
            self.messages[user_id] = deque()
            return True
        now = time.time()
        self._cleanup_window(user_id, now)
        message = self.messages[user_id]
        if len(message) >= self.max_requests:
            return False
        return True

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):
            now = time.time()
            self.messages[user_id].append(now)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        if len(self.messages[user_id]) == 0:
            return 0
        now = time.time()
        time_until_next_allowed = self.size - (now - self.messages[user_id][0])
        return time_until_next_allowed


# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'x (очікування {wait_time:.1f}с)'}")

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'х (очікування {wait_time:.1f}с)'}")
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()