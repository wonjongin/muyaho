import time
from coffee_queue import CoffeeQueue

def TestCoffeeQueue() : 
    print("카페인 중독 과정 시뮬레이션")
    cq = CoffeeQueue(caffeine_threshold=5)

    cq.enqueue("바닐라크림 콜드브루")
    time.sleep(1)
    cq.enqueue("플랫화이트")
    time.sleep(1)
    cq.enqueue("아메리카노")
    time.sleep(1)

    print("카페인 주입 완료")
    time.slepp(1)

    print("\n 카페인 상태 확인")
    cq.print_state()

    print("\n 카페인 과다 대기중")
    time.sleep(10)

    print("\n 최종 상태")
    cq.print_state()

    print("\n 일반 dequeue")
    item = cq.dequeue()
    print(f"일반 dequeue 결과: {item}")

    print("\n 테스트 종료")

if __name__ == "__main__":
    test_coffee_queue()