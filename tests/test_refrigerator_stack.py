import pytest
import time
from muyaho.refrigerator_stack import RefrigeratorStack, FoodEatenException


def test_basic_stack_operations():
    # 기본 스택 작업 테스트
    fridge = RefrigeratorStack(expiry_time=10)
    fridge.push("우유")
    fridge.push("계란")
    fridge.push("치즈")

    assert fridge.size() == 3
    assert fridge.peek() == "치즈"

    item = fridge.pop()
    assert item == "치즈"
    assert fridge.size() == 2

    item = fridge.pop()
    assert item == "계란"
    assert fridge.size() == 1


def test_capacity_limit():
    # 용량 제한 테스트
    fridge = RefrigeratorStack(max_size=3)
    fridge.push("우유")
    fridge.push("계란")
    fridge.push("치즈")
    fridge.push("김치")  # 이것을 추가하면 "우유"가 밀려나야 함

    assert fridge.size() == 3
    # 우유는 이제 찾을 수 없어야 함
    assert fridge.find("우유") is None
    # 하지만 새로 추가한 김치는 있어야 함
    assert fridge.find("김치") == "김치"


def test_find_function():
    # find 함수 테스트
    fridge = RefrigeratorStack()
    fridge.push({"name": "우유", "type": "유제품"})
    fridge.push({"name": "요거트", "type": "유제품"})
    fridge.push({"name": "소고기", "type": "육류"})

    # 람다로 찾기
    dairy = fridge.find(lambda x: x["type"] == "유제품")
    assert dairy["type"] == "유제품"

    # 값으로 찾기
    beef = fridge.find({"name": "소고기", "type": "육류"})
    assert beef["name"] == "소고기"


def test_freshness_decreases():
    # 반복 검색 시 신선도 감소 테스트
    fridge = RefrigeratorStack()
    fridge.push("치즈")

    # 초기 신선도는 10
    assert fridge.get_freshness("치즈") == 10

    # 여러 번 찾으면 신선도 떨어짐
    for _ in range(5):
        try:
            fridge.find("치즈")
        except FoodEatenException:
            pass  # 랜덤 예외는 무시

    # 신선도가 떨어져야 함 (정확한 값은 예외 발생 횟수에 따라 다를 수 있음)
    assert fridge.get_freshness("치즈") < 10


def test_expiry():
    # 유통기한 테스트 (짧은 시간으로 설정)
    fridge = RefrigeratorStack(expiry_time=2)
    fridge.push("금방 상하는 음식")

    # 추가 후 바로 확인
    assert fridge.find("금방 상하는 음식") == "금방 상하는 음식"

    # 유통기한이 지날 때까지 대기
    time.sleep(3)

    # 이제 찾을 수 없어야 함 (유통기한 지남)
    assert fridge.find("금방 상하는 음식") is None


def test_random_exception():
    # 랜덤 예외 발생 테스트
    fridge = RefrigeratorStack()
    fridge.push("사과")

    # 여러 번 시도하면 언젠가 예외가 발생해야 함
    exception_occurred = False
    for _ in range(1000):  # 충분히 많은 시도
        try:
            fridge.find("사과")
        except FoodEatenException:
            exception_occurred = True
            break

    assert (
        exception_occurred
    ), "100번 시도했지만 '누가 이걸 다 먹었어?!' 예외가 발생하지 않음"


def test_empty_fridge():
    # 빈 냉장고 테스트
    fridge = RefrigeratorStack()

    with pytest.raises(IndexError):
        fridge.pop()

    with pytest.raises(IndexError):
        fridge.peek()
