import time
import random
import threading
from typing import Any
from circular_queue import CircularQueue

class CaffeinatedItem:
    def __init__(self, data: Any):
        self.data = data
        self.timestamp = time.time()
        self.caffeine_level = 0  # 시간이 지날수록 증가

class CoffeeQueue:
    """
    실행 시간에 따라 카페인 레벨이 증가하는 원형 큐
    - 오래 대기하면 과카페인 상태로 튀어나옴
    - 아침(앞쪽)에 들어온 요소가 우선 처리됨
    """
    def __init__(self, max_size: int = 100, caffeine_threshold: int = 30):
        self.queue = CircularQueue()
        self.items = [None] * self.queue.MAX_SIZE
        self.front = self.queue.front
        self.rear = self.queue.rear
        self.max_size = max_size
        self.lock = threading.Lock()
        self.caffeine_threshold = caffeine_threshold

        # 카페인 상태 모니터링 쓰레드
        self._thread = threading.Thread(target=self._monitor_caffeine, daemon=True)
        self._thread.start()

    def enqueue(self, item: Any):
        with self.lock:
            wrapped = CaffeinatedItem(item)
            if self.queue.is_full():
                print("⚠️ 큐가 가득 찼습니다.")
                return
            self.queue.enqueue(wrapped)
            self.rear = self.queue.rear
            self.items[self.rear] = wrapped

    def dequeue(self) -> Any:
        with self.lock:
            if self.queue.is_empty():
                print("⚠️ 큐가 비어 있습니다.")
                return None
            item: CaffeinatedItem = self.queue.dequeue()
            self.front = self.queue.front
            return item.data

    def _monitor_caffeine(self):
        """과카페인 상태 요소를 랜덤하게 튀어나오게 함"""
        while True:
            time.sleep(1)
            with self.lock:
                i = self.queue.front
                while i != self.queue.rear:
                    i = (i + 1) % self.queue.MAX_SIZE
                    item: CaffeinatedItem = self.items[i]
                    if item is None:
                        continue

                    # 카페인 레벨 증가
                    item.caffeine_level += 1

                    # 일정 수치 넘으면 랜덤하게 튀어나올 수 있음
                    if item.caffeine_level >= self.caffeine_threshold:
                        if random.random() < 0.3:  # 30% 확률로 튀어나감
                            print(f"💥 과카페인으로 튀어나온 항목: {item.data}")
                            if i == self.queue.front:
                                self.queue.dequeue()
                            else:
                                self.items[i] = None  # 삭제된 것처럼 처리
                time.sleep(1)

    def print_state(self):
        """큐 상태 출력"""
        print("☕ 현재 큐 상태:")
        i = self.queue.front
        while i != self.queue.rear:
            i = (i + 1) % self.queue.MAX_SIZE
            item = self.items[i]
            if item:
                elapsed = int(time.time() - item.timestamp)
                print(f" - {item.data} (카페인: {item.caffeine_level}, 대기: {elapsed}s)")
