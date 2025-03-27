# MuYaHo

A funny python data structure library.

## Features

- Refrigerator Stack (냉장고 스택)
  - 요소들이 뒤로 밀려나서 결국 "잊혀짐"
  - 가장 오래된 데이터는 "유통기한"이 지나 자동 삭제
  - 같은 요소를 두 번 이상 검색하면 "신선도"가 떨어짐
  - 랜덤 접근 시도 시 10% 확률로 "누가 이걸 다 먹었어?!" 예외 발생
