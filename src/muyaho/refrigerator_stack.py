import random
import time
from typing import Any, Dict, List, Optional
import threading


class FoodExpiredException(Exception):
    """유통기한이 지난 음식 예외"""

    pass


class FoodEatenException(Exception):
    """누가 이걸 다 먹었어?! 예외"""

    pass


class RefrigeratorStack:
    """
    냉장고 스택 구현:
    - 요소들이 뒤로 밀려나서 결국 "잊혀짐"
    - 가장 오래된 데이터는 "유통기한"이 지나 자동 삭제
    - 같은 요소를 두 번 이상 검색하면 "신선도"가 떨어짐
    - 랜덤 접근 시도 시 10% 확률로 "누가 이걸 다 먹었어?!" 예외 발생
    """

    def __init__(self, expiry_time: int = 60, max_size: int = 10):
        """
        냉장고 스택 초기화

        Args:
            expiry_time: 유통기한 (초 단위, 기본 60초)
            max_size: 냉장고 최대 크기 (기본 10)
        """
        self._stack: List[Any] = []
        self._timestamps: Dict[int, float] = {}  # 각 요소의 추가된 시간
        self._freshness: Dict[
            int, int
        ] = {}  # 각 요소의 신선도 (낮을수록 신선하지 않음)
        self._expiry_time = expiry_time
        self._max_size = max_size
        self._lock = threading.Lock()

        # 유통기한 체크 스레드 시작
        self._cleanup_thread = threading.Thread(target=self._check_expiry, daemon=True)
        self._cleanup_thread.start()

    def push(self, item: Any) -> None:
        """
        냉장고에 아이템 추가

        Args:
            item: 추가할 아이템
        """
        with self._lock:
            # 냉장고가 가득 찼으면 가장 오래된 항목 제거
            if len(self._stack) >= self._max_size:
                oldest = self._stack.pop(0)
                item_id = id(oldest)
                if item_id in self._timestamps:
                    del self._timestamps[item_id]
                if item_id in self._freshness:
                    del self._freshness[item_id]

            # 새 아이템 추가
            self._stack.append(item)
            self._timestamps[id(item)] = time.time()
            self._freshness[id(item)] = 10  # 초기 신선도 10 (최대)

    def pop(self) -> Any:
        """냉장고에서 가장 최근 아이템 꺼내기"""
        with self._lock:
            if not self._stack:
                raise IndexError("냉장고가 비어있어요!")

            item = self._stack.pop()
            item_id = id(item)

            # 메타데이터 정리
            if item_id in self._timestamps:
                del self._timestamps[item_id]
            if item_id in self._freshness:
                del self._freshness[item_id]

            return item

    def peek(self) -> Any:
        """냉장고의 맨 위 아이템 확인하기 (꺼내지 않음)"""
        with self._lock:
            if not self._stack:
                raise IndexError("냉장고가 비어있어요!")

            return self._stack[-1]

    def find(self, item_match) -> Optional[Any]:
        """
        냉장고에서 아이템 찾기 (람다 함수로 비교 가능)
        찾으면 신선도가 감소함

        Args:
            item_match: 비교할 아이템 또는 비교 함수
        """
        with self._lock:
            if random.random() < 0.1:  # 10% 확률로 예외 발생
                raise FoodEatenException("누가 이걸 다 먹었어?!")

            for item in self._stack:
                if callable(item_match):
                    if item_match(item):
                        # 신선도 감소
                        self._freshness[id(item)] = max(
                            0, self._freshness.get(id(item), 10) - 1
                        )
                        return item
                elif item == item_match:
                    # 신선도 감소
                    self._freshness[id(item)] = max(
                        0, self._freshness.get(id(item), 10) - 1
                    )
                    return item

            return None

    def size(self) -> int:
        """냉장고 내 아이템 개수 반환"""
        with self._lock:
            return len(self._stack)

    def _check_expiry(self) -> None:
        """유통기한이 지난 아이템을 주기적으로 제거하는 백그라운드 메서드"""
        while True:
            time.sleep(1)  # 1초마다 체크

            with self._lock:
                current_time = time.time()
                expired_indices = []

                # 유통기한이 지난 아이템 찾기
                for i, item in enumerate(self._stack):
                    item_id = id(item)
                    if item_id in self._timestamps:
                        item_age = current_time - self._timestamps[item_id]
                        freshness = self._freshness.get(item_id, 10)

                        # 신선도가 낮을수록 유통기한이 빨리 지남
                        adjusted_expiry = self._expiry_time * (freshness / 10)

                        if item_age > adjusted_expiry:
                            expired_indices.append(i)

                # 뒤에서부터 제거 (인덱스 변화 방지)
                for i in sorted(expired_indices, reverse=True):
                    item = self._stack.pop(i)
                    item_id = id(item)
                    if item_id in self._timestamps:
                        del self._timestamps[item_id]
                    if item_id in self._freshness:
                        del self._freshness[item_id]

    def get_freshness(self, item) -> int:
        """아이템의 현재 신선도 반환 (0-10, 높을수록 신선)"""
        with self._lock:
            for fridge_item in self._stack:
                if fridge_item == item:
                    return self._freshness.get(id(fridge_item), 0)
            return 0

    def get_expiry_time(self, item) -> Optional[float]:
        """아이템의 남은 유통기한 시간 반환 (초 단위)"""
        with self._lock:
            for fridge_item in self._stack:
                if fridge_item == item:
                    item_id = id(fridge_item)
                    if item_id in self._timestamps:
                        freshness = self._freshness.get(item_id, 10)
                        adjusted_expiry = self._expiry_time * (freshness / 10)
                        elapsed = time.time() - self._timestamps[item_id]
                        return max(0, adjusted_expiry - elapsed)
            return None
