import time
import random
from typing import Any
from .circular_queue import CircularQueue

class CaffeinatedTask:
    def __init__(self, data: Any):
        self.data = data
        self.caffeine_level = 0
        self.timestamp = time.time()

class CoffeeQueue:
    def __init__(self, max_size: int = 100, caffeine_threshold: int = 30):
        self.coffee_queue = CircularQueue()
        self.task_queue = CircularQueue()
        self.caffeine_threshold = caffeine_threshold
        self.caffeine_level = 0
        self.bounced_tasks = []
        self.completed_tasks = []

    def enqueue_coffee(self, coffee: Any):
        if self.coffee_queue.is_full():
            print("⚠️ 커피 큐가 가득 찼습니다.")
            return
        self.coffee_queue.enqueue(coffee)
        self.caffeine_level += 1
        print(f"☕ 복용 카페인: {coffee} (현재 수치: {self.caffeine_level})")

    def enqueue_task(self, task: Any):
        if self.task_queue.is_full():
            print("⚠️ 과제 큐가 가득 찼습니다.")
            return
        self.task_queue.enqueue(CaffeinatedTask(task))
        print(f"📝 수행 과제 추가: {task}")

    def process_tasks(self):
        print("▶ 과제 수행 시작")
        temp_queue = CircularQueue()

        while not self.task_queue.is_empty():
            task: CaffeinatedTask = self.task_queue.dequeue()
            task.caffeine_level += self.caffeine_level

            if task.caffeine_level >= self.caffeine_threshold:
                if random.random() < 0.3:
                    print(f"💥 과카페인 상태로 튕긴 과제: {task.data}")
                    self.bounced_tasks.append(task.data)
                    continue

            print(f"✅ 과제 수행 완료: {task.data}")
            self.completed_tasks.append(task.data)

        self.task_queue = temp_queue
        print("✅ 모든 과제 처리 완료")

    def print_state(self):
        print("\n📦 현재 큐 상태:")
        print(f" - 카페인 수치: {self.caffeine_level}")
        print(f" - 수행 완료 과제: {self.completed_tasks}")
        print(f" - 튕긴 과제: {self.bounced_tasks}")