# MuYaHo

A funny python data structure library.

## Features

- Refrigerator Stack (냉장고 스택)
  - 요소들이 뒤로 밀려나서 결국 "잊혀짐"
  - 가장 오래된 데이터는 "유통기한"이 지나 자동 삭제
  - 같은 요소를 두 번 이상 검색하면 "신선도"가 떨어짐
  - 랜덤 접근 시도 시 10% 확률로 "누가 이걸 다 먹었어?!" 예외 발생

- Coffee Queue(커피 큐)
  - 커피를 마실수록 카페인 수치가 증가
  - 카페인 수치가 임계치 넘으면, 과제 무작위로 튕겨져 나감
  - 먼저 삽입된 과제 빨리 처리

- Assignment Queue (과제 큐)
  - 지원이는 과제를 해야 함
  - 과제 큐에 과제가 매주 화요일, 수요일일, 금요일에 새로 생김
  - 화, 수에 들어오는 과제는 기한이 일주일, 금에 생기는 과제는 기간이 2주
  - 지원이는 과제를 기한이 가까운 것부터 함
  - 모든 과제가 기한이 4일 이상 남으면 하루 전으로 미룸
  - 하루에 처리해야 하는 과제가 3개 이상이면 휴학
