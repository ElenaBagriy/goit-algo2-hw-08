import time
from typing import Dict
import random

class ThrottlingRateLimiter:
    def __init__(self, min_interval: float = 10.0):
        self.min_interval = min_interval
        self.messages: Dict[str, float] = {}

    def can_send_message(self, user_id: str) -> bool:
        if user_id not in self.messages:
            return True
        now = time.time()
        last_message = self.messages[user_id]
        if now - last_message >= self.min_interval:
            return True
        return False

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):
            self.messages[user_id] = time.time()
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        now = time.time()
        if user_id not in self.messages:
            return 0
        last_message = self.messages[user_id]
        time_until_next_allowed = self.min_interval - (now - last_message)
        if time_until_next_allowed <= 0:
            return 0
        return time_until_next_allowed


def test_throttling_limiter():
    limiter = ThrottlingRateLimiter(min_interval=10.0)

    print("\\n=== Симуляція потоку повідомлень (Throttling) ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Випадкова затримка між повідомленнями
        time.sleep(random.uniform(0.1, 1.0))

    print("\\nОчікуємо 10 секунд...")
    time.sleep(10)

    print("\\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_throttling_limiter()
