import datetime
from enum import Enum
import copy
from .circular_queue import CircularQueue

class Date(Enum):
    TUESDAY   = 1
    WEDNESDAY = 2
    FRIDAY    = 3

class AssignmentQueue:
    def __init__(self, day: Date, create_date: datetime.date):
        self.day = day
        self.create_date = create_date
        if day in (Date.TUESDAY, Date.WEDNESDAY):
            self.deadline = create_date + datetime.timedelta(days=7)
        else:
            self.deadline = create_date + datetime.timedelta(days=14)

    def left_days(self, current_date: datetime.date) -> int:
        return (self.deadline - current_date).days

    def __str__(self) -> str:
        return f"마감일: {self.deadline.strftime('%Y-%m-%d')}"


class AssignmentManager:
    def __init__(self):
        self.assignment_queue = CircularQueue()
        self.current_date = datetime.date.today()
        self.took_leave = False

    def add_task(self, day: Date) -> None:
        assignment = AssignmentQueue(day, self.current_date)
        self.assignment_queue.enqueue(assignment)
        print(f"새 과제 추가: {assignment}")

    def process_day(self) -> None:
        if self.took_leave:
            print("이미 휴학했습니다.")
            return

        dow = self.current_date.weekday()  # 0=Mon,1=Tue,...

        # 1) 자동 과제 추가
        if dow == 1:
            self.add_task(Date.TUESDAY)
        elif dow == 2:
            self.add_task(Date.WEDNESDAY)
        elif dow == 4:
            self.add_task(Date.FRIDAY)

        # 2) 큐 비어있으면 하루만 스킵
        if self.assignment_queue.is_empty():
            self.current_date += datetime.timedelta(days=1)
            return

        # 3) 오늘 처리할 과제들 모두 꺼내기
        tasks = []
        while not self.assignment_queue.is_empty():
            tasks.append(self.assignment_queue.dequeue())
        n = len(tasks)

        # 4) 과제 3개 이상이면 휴학
        if n >= 3:
            print(f"과제 {n}개로 3개 이상이므로 휴학합니다.")
            self.took_leave = True
            for t in tasks:
                self.assignment_queue.enqueue(t)
            return

        # 5) 단일 과제이고 여유 >= 4일이면 3일 미루기
        if n == 1 and tasks[0].left_days(self.current_date) >= 4:
            print("단일 과제이고 여유 있으니 3일 미룹니다.")
            self.assignment_queue.enqueue(tasks[0])
            self.current_date += datetime.timedelta(days=3)
            return

        # 6) 그 외(과제 2개 이하) → 기한 가까운 순 처리(최대 2개)
        tasks.sort(key=lambda t: t.left_days(self.current_date))
        cnt = min(2, n)
        for i in range(cnt):
            print(f"과제 완료: {tasks[i]}")
        for i in range(cnt, n):
            self.assignment_queue.enqueue(tasks[i])

        # 하루 경과
        self.current_date += datetime.timedelta(days=1)

    def fast_forward(self, days: int) -> None:
        # 첫날에 큐가 비어 있으면 곧바로 days만큼 건너뜀
        if self.assignment_queue.is_empty():
            self.current_date += datetime.timedelta(days=days)
            return

        # 아니라면 하루씩 process_day 실행
        for _ in range(days):
            print(f"\n===== {self.current_date.strftime('%Y-%m-%d')} =====")
            self.process_day()
            if self.took_leave:
                break

    def status(self) -> None:
        print(f"\n현재 날짜: {self.current_date.strftime('%Y-%m-%d')}")
        print("남은 과제 목록:")
        if self.assignment_queue.is_empty():
            print(" 없음")
            return

        temp = CircularQueue()
        tasks = []
        while not self.assignment_queue.is_empty():
            t = self.assignment_queue.dequeue()
            tasks.append(t)
            temp.enqueue(t)
        self.assignment_queue = copy.deepcopy(temp)

        for t in sorted(tasks, key=lambda x: x.left_days(self.current_date)):
            ld = t.left_days(self.current_date)
            print(f"  마감까지 {ld}일 남음 ({t.deadline.strftime('%Y-%m-%d')})")
