import time
from coffee_queue import CoffeQueue
from threading import Thread

def TestCoffeeQueue():
    coffee_queue = CoffeeQueue(max_size=5, caffeine_threshold=5)

    coffee_queue.enqueue_coffee("아메리카노")
    coffee_queue.enqueue_coffee("플랫화이트")
    coffee_queue.enqueue_coffee("바닐라크림 콜드브루")
    coffee_queue.enqueue_coffee("모카")
    coffee_queue.enqueue_coffee("카푸치노")

    coffee_queue.enqueue_task("과제1")
    coffee_queue.enqueue_task("과제2")
    coffee_queue.enqueue_task("과제3")
    coffee_queue.enqueue_task("과제4")

    for _ in range(10) : 
        time.sleep(1)
        coffee_queue.print_state()

        task = coffee_queue.dequeue_task()
        if task : 
            print(f"처리한 과제 : {task}")
        
test_thread = Thread(target = TestCoffeeQueue)
test_thread.start()

test_thread.join()