# 🧭 여행 일정 추천 챗봇, TripChat
## 프로젝트 소개
> 새로 찾아가는 여행지에서 좋은 관광지와 맛집을 시간에 맞춰 가는 것은 매우 번거로운 일입니다. 카카오맵과 네이버 지도 등을 활용하여 평점, 영업시간, 휴무일, 거리, 교통수단, 체류 시간 등 많은 조건들을 생각해야 합니다.
>
> 본 서비스는 사용자의 현재 위치, 체력 수준, 음식 선호도, 가용 시간 등 개인화된 조건을 입력받아 최적의 여행 코스를 제안합니다. 공공데이터와 웹 검색을 활용해 관광명소와 맛집에 대한 정보를 확인하고 실시간 데이터를 기반으로 더욱 정확한 정보를 제공하고자 합니다. 사용자들의 후기 데이터를 수집하여 서비스 품질을 지속적으로 개선하며, 이를 통해 관광지 개선에도 기여할 수 있는 선순환 구조를 만들어갑니다.

## 사용법
1. 원하는 목적지와 도착 시간을 포함하여 챗봇에게 질문합니다.
2. 답을 얻은 후, 추가적인 정보를 제공하여 더욱 자세한 일정을 계획합니다.

## 배포된 링크
[TripChat 바로가기](https://tripchat.vercel.app/)

## 로컬 실행 방법
1. (선택) 가상환경 설정
    - `cd back`
    - `python -m venv venv` : 가상환경 생성
    - `source venv/Scripts/activate` : 가상환경 활성화

2. `pip install -r requirements.txt`로 필요 라이브러리 설치

3. **.env** 파일 생성 후 **.env.example** 파일을 참고하여 API KEY 설정

3. `python app.py`로 파일 실행 (계속 실행 유지!)

4. 새로운 터미널에서 `cd front`로 이동 후
    - `npm i`
    - `npm start`
