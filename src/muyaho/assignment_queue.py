import datetime
from enum import Enum
from typing import Optional, List
import copy
from circular_queue import CircularQueue

class TaskDay(Enum):
    TUESDAY = 1
    WEDNESDAY = 2
    FRIDAY = 3


class AssignmentQueue:
    """과제 클래스"""
    
    def __init__(self, name: str, day: TaskDay, create_date: datetime.date):
        """
        과제 초기화
        
        Args:
            name: 과제 이름
            day: 과제가 주어진 요일
            create_date: 과제가 생성된 날짜
        """
        self.name = name
        self.day = day
        self.create_date = create_date
        
        # 과제 마감일 계산
        if day in [TaskDay.TUESDAY, TaskDay.WEDNESDAY]:
            # 화요일과 수요일 과제는 1주일 후가 마감
            self.deadline = create_date + datetime.timedelta(days=7)
        else:
            # 금요일 과제는 2주일 후가 마감
            self.deadline = create_date + datetime.timedelta(days=14)
    
    def days_left(self, current_date: datetime.date) -> int:
        """현재 날짜로부터 마감일까지 남은 일수 반환"""
        return (self.deadline - current_date).days
    
    def __str__(self) -> str:
        return f"과제: {self.name}, 마감일: {self.deadline.strftime('%Y-%m-%d')}"


class TaskManager:
    """과제 관리 시스템"""
    
    def __init__(self):
        """과제 관리 시스템 초기화"""
        self.task_queue = CircularQueue()
        self.current_date = datetime.date.today()
        self.took_leave = False  # 휴학 여부
    
    def add_task(self, name: str, day: TaskDay) -> None:
        """
        새로운 과제 추가
        
        Args:
            name: 과제 이름
            day: 과제가 주어진 요일
        """
        task = Task(name, day, self.current_date)
        self.task_queue.enqueue(task)
        print(f"새 과제 추가: {task}")
    
    def process_day(self) -> None:
        """하루의 과제 처리"""
        if self.took_leave:
            print("이미 휴학했습니다.")
            return
        
        # 오늘의 요일 확인 (0:월요일, 1:화요일, ..., 6:일요일)
        weekday = self.current_date.weekday()
        
        # 화요일, 수요일, 금요일에는 새 과제 자동 추가
        if weekday == 1:  # 화요일
            self.add_task(f"화요일 과제 {self.current_date}", TaskDay.TUESDAY)
        elif weekday == 2:  # 수요일
            self.add_task(f"수요일 과제 {self.current_date}", TaskDay.WEDNESDAY)
        elif weekday == 4:  # 금요일
            self.add_task(f"금요일 과제 {self.current_date}", TaskDay.FRIDAY)
        
        # 오늘 처리할 과제 목록 구성
        tasks_today = []
        temp_queue = CircularQueue()
        
        # 모든 과제가 기한이 4일 이상 남았는지 확인하는 플래그
        all_tasks_have_4days_or_more = True
        
        # 큐에서 모든 과제를 가져와 기한 확인
        while not self.task_queue.is_empty():
            task = self.task_queue.dequeue()
            days_left = task.days_left(self.current_date)
            
            if days_left < 4:
                all_tasks_have_4days_or_more = False
            
            temp_queue.enqueue(task)
        
        # 원래 큐로 복원
        self.task_queue = copy.deepcopy(temp_queue)
        
        # 모든 과제가 4일 이상 남았으면 하루 미룸
        if all_tasks_have_4days_or_more and not self.task_queue.is_empty():
            print("모든 과제가 4일 이상 남았습니다. 오늘 과제는 미룹니다.")
            self.current_date += datetime.timedelta(days=1)
            return
        
        # 처리해야 할 과제 목록 생성 (기한이 가까운 순)
        tasks_to_process = []
        temp_queue = CircularQueue()
        
        while not self.task_queue.is_empty():
            task = self.task_queue.dequeue()
            tasks_to_process.append(task)
        
        # 기한이 가까운 순으로 정렬
        tasks_to_process.sort(key=lambda t: t.days_left(self.current_date))
        
        # 3개 이상이면 휴학
        if len(tasks_to_process) >= 3:
            print(f"오늘 처리해야 할 과제가 {len(tasks_to_process)}개로 3개 이상입니다. 휴학을 결정했습니다.")
            self.took_leave = True
            return
        
        # 과제 처리 (최대 2개)
        processed_count = min(2, len(tasks_to_process))
        for i in range(processed_count):
            task = tasks_to_process[i]
            print(f"과제 완료: {task}")
        
        # 남은 과제 다시 큐에 넣기
        for i in range(processed_count, len(tasks_to_process)):
            self.task_queue.enqueue(tasks_to_process[i])
        
        # 하루 증가
        self.current_date += datetime.timedelta(days=1)
    
    def fast_forward(self, days: int) -> None:
        """
        지정된 일수만큼 시간을 진행
        
        Args:
            days: 진행할 일수
        """
        for _ in range(days):
            print(f"\n===== {self.current_date.strftime('%Y-%m-%d')} =====")
            self.process_day()
            if self.took_leave:
                break
    
    def status(self) -> None:
        """현재 과제 상태 출력"""
        print(f"\n현재 날짜: {self.current_date.strftime('%Y-%m-%d')}")
        print("남은 과제 목록:")
        
        if self.task_queue.is_empty():
            print("  없음")
            return
        
        temp_queue = CircularQueue()
        tasks = []
        
        while not self.task_queue.is_empty():
            task = self.task_queue.dequeue()
            tasks.append(task)
            temp_queue.enqueue(task)
        
        # 큐 복원
        self.task_queue = copy.deepcopy(temp_queue)
        
        # 기한이 가까운 순으로 정렬해서 출력
        for task in sorted(tasks, key=lambda t: t.days_left(self.current_date)):
            days = task.days_left(self.current_date)
            print(f"  {task.name} - 마감까지 {days}일 남음 ({task.deadline.strftime('%Y-%m-%d')})")


# 사용 예시
if __name__ == "__main__":
    manager = TaskManager()
    
    # 몇 가지 초기 과제 추가
    manager.add_task("프로그래밍 과제", TaskDay.TUESDAY)
    manager.add_task("수학 과제", TaskDay.WEDNESDAY)
    
    # 상태 확인
    manager.status()
    
    # 일주일 진행
    manager.fast_forward(7)
    
    # 최종 상태 확인
    manager.status()
