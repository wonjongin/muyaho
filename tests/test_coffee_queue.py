import time
import random
from muyaho.coffee_queue import CoffeeQueue
from muyaho.circular_queue import CircularQueue

# 큐 길이 계산용
def queue_length(queue):
    return (queue.rear - queue.front + queue.MAX_SIZE) % queue.MAX_SIZE

def test_basic_coffee_queue_operations(monkeypatch):
    monkeypatch.setattr(random, "random", lambda: 1.0)
    q = CoffeeQueue(max_size=5, caffeine_threshold=3)

    q.enqueue_coffee("아메리카노")
    q.enqueue_coffee("라떼")
    q.enqueue_coffee("콜드브루")
    assert q.caffeine_level == 3

    q.enqueue_task("과제1")
    q.enqueue_task("과제2")
    assert queue_length(q.task_queue) == 2

    q.process_tasks()
    assert "과제1" in q.completed_tasks
    assert "과제2" in q.completed_tasks
    assert len(q.bounced_tasks) == 0

def test_task_bounce(monkeypatch):
    monkeypatch.setattr(random, "random", lambda: 0.0)  # 항상 튕기게
    q = CoffeeQueue(max_size=5, caffeine_threshold=1)

    q.enqueue_coffee("더블샷")
    q.enqueue_task("과제1")
    q.enqueue_task("과제2")

    q.process_tasks()
    assert len(q.completed_tasks) == 0
    assert "과제1" in q.bounced_tasks
    assert "과제2" in q.bounced_tasks

def test_mixed_behavior(monkeypatch):
    monkeypatch.setattr(random, "random", lambda: 0.5)  # 안 튕김
    q = CoffeeQueue(max_size=5, caffeine_threshold=2)

    q.enqueue_coffee("아침커피")
    q.enqueue_coffee("점심커피")
    q.enqueue_task("레포트 작성")

    q.process_tasks()
    assert "레포트 작성" in q.completed_tasks
    assert len(q.bounced_tasks) == 0

def test_print_state(monkeypatch, capsys):
    monkeypatch.setattr(random, "random", lambda: 1.0)
    q = CoffeeQueue(max_size=5, caffeine_threshold=2)
    q.enqueue_coffee("라떼")
    q.enqueue_coffee("아포가토")
    q.enqueue_task("슬라이드 준비")
    q.process_tasks()
    q.print_state()

    captured = capsys.readouterr()
    assert "슬라이드 준비" in captured.out
    assert "카페인 수치" in captured.out