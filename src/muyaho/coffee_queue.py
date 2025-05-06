import time
import random
import threading
from typing import Any
from circular_queue import CircularQueue

class CaffeinatedTask:
    def __init__(self, task: Any):
        self.task = task
        self.timestamp = time.time()
        self.caffeine_level = 0  # 시간이 지날수록 증가

class CoffeeQueue:
    """
    커피 주입과 과제 큐를 분리하여 과제가 과카페인 상태로 처리되는 원형 큐
    - 커피 큐는 커피를 넣는 곳
    - 과제 큐는 과제가 쌓여서 처리되는 곳
    - 과제 큐의 항목이 과카페인 상태가 되면 우선 처리 큐로 이동하거나 랜덤하게 튕겨져 나간다.
    """
    def __init__(self, max_size: int = 100, caffeine_threshold: int = 30):
        # 커피와 과제 큐를 따로 관리
        self.coffee_queue = CircularQueue()
        self.task_queue = CircularQueue()
        
        self.max_size = max_size
        self.lock = threading.Lock()
        self.caffeine_threshold = caffeine_threshold

        # 과카페인 상태 처리 전용 큐
        self.priority_queue = []

        # 카페인 상태 모니터링 쓰레드
        self._thread = threading.Thread(target=self._monitor_caffeine, daemon=True)
        self._thread.start()

    def enqueue_coffee(self, coffee: Any):
        """커피 큐에 커피 주입"""
        with self.lock:
            if self.coffee_queue.is_full():
                print("⚠️ 커피 큐가 가득 찼습니다.")
                return
            self.coffee_queue.enqueue(coffee)
            print(f"☕ 커피가 큐에 주입되었습니다: {coffee}")

    def enqueue_task(self, task: Any):
        """과제 큐에 과제 추가"""
        with self.lock:
            wrapped = CaffeinatedTask(task)
            if self.task_queue.is_full():
                print("⚠️ 과제 큐가 가득 찼습니다.")
                return
            self.task_queue.enqueue(wrapped)
            print(f"📚 과제가 큐에 추가되었습니다: {task}")

    def dequeue_task(self) -> Any:
        """우선 처리 큐가 있으면 우선 처리 큐에서 과제 처리"""
        with self.lock:
            if self.priority_queue:  # 우선 처리 큐가 있으면
                item = self.priority_queue.pop(0)
                print(f"🔥 우선 처리 큐에서 과제 처리: {item.task}")
                return item.task

            if self.task_queue.is_empty():
                print("⚠️ 과제 큐가 비어 있습니다.")
                return None
            item: CaffeinatedTask = self.task_queue.dequeue()
            return item.task

    def _monitor_caffeine(self):
        """과카페인 상태 요소를 랜덤하게 튀어나오게 함"""
        while True:
            time.sleep(1)
            with self.lock:
                i = self.task_queue.front
                while i != self.task_queue.rear:
                    i = (i + 1) % self.task_queue.MAX_SIZE
                    item: CaffeinatedTask = self.task_queue.items[i]
                    if item is None:
                        continue

                    # 카페인 레벨 증가
                    item.caffeine_level += 1

                    # 일정 수치 넘으면 랜덤하게 튕겨나가거나 우선 처리 큐로 이동
                    if item.caffeine_level >= self.caffeine_threshold:
                        if random.random() < 0.3:  # 30% 확률로 튕겨나감
                            print(f"💥 과카페인으로 튕겨 나온 과제: {item.task}")
                            self.task_queue.dequeue()  # 큐에서 튕겨 나옴
                        else:
                            # 우선 처리 큐에 넣어 놓기
                            print(f"🔥 과카페인 상태로 우선 처리 큐에 추가된 과제: {item.task}")
                            self.priority_queue.append(item)
                time.sleep(1)

    def print_state(self):
        """큐 상태 출력"""
        print("☕ 커피 큐 상태:")
        i = self.coffee_queue.front
        while i != self.coffee_queue.rear:
            i = (i + 1) % self.coffee_queue.MAX_SIZE
            item = self.coffee_queue.items[i]
            if item:
                print(f" - 커피: {item}")

        print("📚 과제 큐 상태:")
        i = self.task_queue.front
        while i != self.task_queue.rear:
            i = (i + 1) % self.task_queue.MAX_SIZE
            item = self.task_queue.items[i]
            if item:
                elapsed = int(time.time() - item.timestamp)
                print(f" - 과제: {item.task} (카페인: {item.caffeine_level}, 대기: {elapsed}s)")
