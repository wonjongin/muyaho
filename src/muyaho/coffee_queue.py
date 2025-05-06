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
    - 과제가 모두 처리되면 '과제 완료' 출력
    - 과카페인 상태로 모든 과제가 튕겨지면 '방전' 출력
    """
    def __init__(self, max_size: int = 100, caffeine_threshold: int = 30):
        self.queue = CircularQueue()
        self.items = [None] * self.queue.MAX_SIZE
        self.front = self.queue.front
        self.rear = self.queue.rear
        self.max_size = max_size
        self.lock = threading.Lock()
        self.caffeine_threshold = caffeine_threshold
        self.tasks_remaining = 0  # 남은 과제 수 추적

        # 카페인 상태 모니터링 쓰레드
        self._thread = threading.Thread(target=self._monitor_caffeine, daemon=True)
        self._thread.start()

    def enqueue_coffee(self, coffee: Any):
        """커피 항목을 큐에 추가"""
        with self.lock:
            wrapped = CaffeinatedItem(coffee)
            if self.queue.is_full():
                print("⚠️ 큐가 가득 찼습니다.")
                return
            self.queue.enqueue(wrapped)
            self.rear = self.queue.rear
            self.items[self.rear] = wrapped

    def enqueue_task(self, task: Any):
        """과제를 큐에 추가"""
        with self.lock:
            wrapped = CaffeinatedItem(task)
            if self.queue.is_full():
                print("⚠️ 큐가 가득 찼습니다.")
                return
            self.queue.enqueue(wrapped)
            self.rear = self.queue.rear
            self.items[self.rear] = wrapped
            self.tasks_remaining += 1  # 과제 수 증가

    def dequeue_task(self) -> Any:
        """과제를 처리"""
        with self.lock:
            if self.queue.is_empty():
                print("⚠️ 큐가 비어 있습니다.")
                return None
            item: CaffeinatedItem = self.queue.dequeue()
            self.front = self.queue.front
            self.tasks_remaining -= 1  # 과제 수 감소
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

            # 과제가 모두 처리되었는지 확인
            if self.tasks_remaining == 0:
                print("✅ 과제 완료")
            
            # 모든 과제가 과카페인 상태로 튕겨져 나가면 방전 처리
            if self.tasks_remaining == 0 and all(item is None for item in self.items):
                print("⚡ 기절")
                break  # 방전 후 종료하거나 원하는 대로 처리

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
