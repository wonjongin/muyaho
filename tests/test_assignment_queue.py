import pytest
import datetime
from enum import Enum
import copy
from muyaho.circular_queue import CircularQueue
from muyaho.assignment_queue import AssignmentQueue, AssignmentManager, Date

class TestAssignmentQueue:
    def test_deadline_calculation(self):
        # 화요일/수요일 과제 마감일 계산 테스트 (7일 후)
        create_date = datetime.date(2023, 5, 15)  # 임의의 날짜
        tuesday_assignment = AssignmentQueue(Date.TUESDAY, create_date)
        assert tuesday_assignment.deadline == create_date + datetime.timedelta(days=7)
        
        wednesday_assignment = AssignmentQueue(Date.WEDNESDAY, create_date)
        assert wednesday_assignment.deadline == create_date + datetime.timedelta(days=7)
        
        # 금요일 과제 마감일 계산 테스트 (14일 후)
        friday_assignment = AssignmentQueue(Date.FRIDAY, create_date)
        assert friday_assignment.deadline == create_date + datetime.timedelta(days=14)

    def test_left_days_calculation(self):
        create_date = datetime.date(2023, 5, 15)
        assignment = AssignmentQueue(Date.TUESDAY, create_date)
        deadline = create_date + datetime.timedelta(days=7)  # 마감일
        
        # 시작일에는 7일 남음
        assert assignment.left_days(create_date) == 7
        
        # 중간 날짜에는 남은 일수가 정확히 계산됨
        middle_date = create_date + datetime.timedelta(days=3)
        assert assignment.left_days(middle_date) == 4
        
        # 마감일에는 0일 남음
        assert assignment.left_days(deadline) == 0
        
        # 마감일 이후에는 음수로 표시
        overdue_date = deadline + datetime.timedelta(days=2)
        assert assignment.left_days(overdue_date) == -2

    def test_string_representation(self):
        create_date = datetime.date(2023, 5, 15)
        assignment = AssignmentQueue(Date.TUESDAY, create_date)
        expected_str = f"마감일: {(create_date + datetime.timedelta(days=7)).strftime('%Y-%m-%d')}"
        assert str(assignment) == expected_str


class TestAssignmentManager:
    def test_add_task(self):
        # 현재 날짜를 고정하기 위한 설정
        fixed_date = datetime.date(2023, 5, 15)
        manager = AssignmentManager()
        manager.current_date = fixed_date
        
        # 과제 추가 전 큐는 비어있어야 함
        assert manager.assignment_queue.is_empty()
        
        # 과제 추가
        manager.add_task(Date.TUESDAY)
        
        # 큐에 과제가 추가되었는지 확인
        assert not manager.assignment_queue.is_empty()
        
        # 큐에서 과제를 추출하여 검증
        task = manager.assignment_queue.dequeue()
        assert task.day == Date.TUESDAY
        assert task.create_date == fixed_date

    def test_process_day_automatic_task_addition(self):
        # 화요일로 날짜 설정
        tuesday = datetime.date(2023, 5, 16)  # 화요일이라고 가정
        
        manager = AssignmentManager()
        manager.current_date = tuesday
        
        # 과제 처리 실행
        manager.process_day()
        
        # 화요일에는 화요일 과제가 자동으로 추가되었는지 확인
        assert not manager.assignment_queue.is_empty()
        
        # 날짜가 하루 증가했는지 확인
        assert manager.current_date == tuesday + datetime.timedelta(days=3)

    def test_take_leave_when_many_tasks(self):
        manager = AssignmentManager()
        current_date = datetime.date(2023, 5, 15)
        manager.current_date = current_date
        
        # 과제 마감일이 1일 이하로 남도록 설정
        past_date = current_date - datetime.timedelta(days=6)  # 화/수 과제의 경우 7일 마감
        
        # 3개 이상의 과제 추가 (기한이 1일 이하로 남은 과제 3개)
        for _ in range(3):
            assignment = AssignmentQueue(Date.TUESDAY, past_date)
            manager.assignment_queue.enqueue(assignment)
        
        # 과제 처리 실행
        manager.process_day()
        
        # 휴학 상태가 되었는지 확인
        assert manager.took_leave == True


    def test_postpone_when_all_tasks_have_enough_time(self):
        manager = AssignmentManager()
        manager.current_date = datetime.date(2023, 5, 15)
        
        # 모든 과제가 여유로운 경우를 만들기 위해 여유 있는 과제 추가
        assignment = AssignmentQueue(Date.TUESDAY, manager.current_date)
        manager.assignment_queue.enqueue(assignment)
        
        # 과제 처리 실행
        manager.process_day()
        
        # 모든 과제가 4일 이상 남아 있으면 3일 미루기
        assert manager.current_date == datetime.date(2023, 5, 18)  # 3일 뒤

    def test_take_leave_when_many_tasks(self):
        manager = AssignmentManager()
        manager.current_date = datetime.date(2023, 5, 15)
        
        # 3개 이상의 과제 추가 (휴학 조건)
        for _ in range(3):
            assignment = AssignmentQueue(Date.TUESDAY, manager.current_date)
            manager.assignment_queue.enqueue(assignment)
        
        # 과제 처리 실행
        manager.process_day()
        
        # 휴학 상태가 되었는지 확인
        assert manager.took_leave == True
        
        # 휴학 후에는 과제 큐가 그대로 유지
        assert not manager.assignment_queue.is_empty()

    def test_process_normal_case(self):
        manager = AssignmentManager()
        manager.current_date = datetime.date(2023, 5, 15)
        
        # 2개의 과제 추가 (정상 처리 가능)
        for _ in range(2):
            assignment = AssignmentQueue(Date.TUESDAY, manager.current_date)
            manager.assignment_queue.enqueue(assignment)
        
        # 과제 처리
        manager.process_day()
        
        # 2개의 과제가 처리되어 큐가 비어있어야 함
        assert manager.assignment_queue.is_empty()
        
        # 날짜가 하루 증가
        assert manager.current_date == datetime.date(2023, 5, 16)
        
        # 휴학 상태가 아니어야 함
        assert manager.took_leave == False

    def test_fast_forward(self):
        manager = AssignmentManager()
        manager.current_date = datetime.date(2023, 5, 15)
        
        # 5일 진행
        manager.fast_forward(5)
        
        # 날짜가 5일 증가했는지 확인
        assert manager.current_date == datetime.date(2023, 5, 20)
        
        # 휴학 시 빠른 진행 중단 확인
        manager = AssignmentManager()
        manager.current_date = datetime.date(2023, 5, 15)
        
        # 휴학 상황 재현을 위해 3개 과제 추가
        for _ in range(3):
            assignment = AssignmentQueue(Date.TUESDAY, manager.current_date)
            manager.assignment_queue.enqueue(assignment)
        
        # 10일 진행 시도 (휴학으로 중단되어야 함)
        manager.fast_forward(10)
        
        # 첫날에 휴학했으므로 날짜가 증가하지 않아야 함
        assert manager.current_date == datetime.date(2023, 5, 15)
        assert manager.took_leave == True
