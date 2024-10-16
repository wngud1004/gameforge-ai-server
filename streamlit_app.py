import streamlit as st
from openai import OpenAI
from fastapi import FastAPI
import requests
import json
import random
import logging


# Show title and description.
# https://gameforge-ai-server.streamlit.app/?token=YOUR_ACCESS_TOKEN
st.title("💬 Chatbot")
st.write(
    "이건 gamefoge 사이트의 챗봇입니다. 모르는 것을 물어보고 원하는 답을 얻어보세요!"
    "오늘의 추천 게임, 공지사항, 문의사항 등 다 가능합니다."
    "재밌는 채팅하시고 gamefoge에서 관련 게임을 구매해보세요!"
)

app = FastAPI()
logging.basicConfig(level=logging.INFO)  # 로그 레벨을 설정합니다 (DEBUG, INFO, WARNING, ERROR, CRITICAL)

# 로그 메시지 전송 함수
def log_message(message):
    logging.info(message)

query_params = st.experimental_get_query_params()
auth_token = query_params.get("token", [None])[0]  # 'token' 매개변수를 가져옴

if auth_token:
    st.session_state.auth_token = auth_token  # 인증 토큰을 세션 상태에 저장
    log_message("인증 토큰이 성공적으로 받아졌습니다. " + auth_token)
else:
    log_message("로그인 하지 않은 상태입니다.")

# Create an OpenAI client.
client = OpenAI(api_key=st.secrets["openai_api_key"])



# https://ludorium.store/api/user/login

user_info_url = "https://ludorium.store/api/user/mypage"
user_library_url = "https://ludorium.store/api/user/library/list"
game_list_url = ""
headers = {
    "Authorization": f"Bearer {auth_token}"  # Bearer 방식으로 Access Token 전달
}

# 사용자 정보 GET 요청
response = requests.get(user_info_url, headers=headers, verify=False)
            
if response.status_code == 200:
    data = response.json()
                
    # 사용자 목록 출력
    print(data)
    print("사용자 정보")
    for user in data['data']['content']:  # 'content' 안에 사용자 데이터가 있다고 가정
        print(f"이메일: {user['email']}, 닉네임: {user['nickname']}, 가입 날짜: {user['regDate']}, 역할: {user['role']}")
    else:
        print(f"사용자 목록 API 요청에 실패했습니다. 상태 코드: {response.status_code}")

custom_prompt = "당신은 주어진 데이터를 바탕으로 유용하고 도움이되는 정확한 답변을 제공하는 게임 어시스턴트입니다."
game_data = '''
{
"Notice": [
    {
    "도움말": "상점 탭에서 게임으로 들어가 장바구니 버튼을 누르면 게임 구매 가능"
    "문의처": "gameforge@gmail.com"
    "사이트 개발자": "윤명철, 신성용, 이인지, 박건후, 김민선"
    "개발일": "2024-10-3"
    }
],
"games": [
    {
      "title": "사이버펑크 2077",
      "developer": "CD 프로젝트 레드",
      "release_date": "2020-12-10",
      "genre": "액션 RPG",
      "price": 59900,
      "platforms": ["PC", "PS5", "Xbox 시리즈 X"],
      "rating": 4.5,
      "description": "플레이어 주도형 내러티브를 특징으로 하는 나이트 시티를 배경으로 한 미래형 오픈 월드 RPG.",
      "image_url": "",
      "game_url": ""
    },
    {
      "title": "더 위쳐 3: 와일드 헌트",
      "developer": "CD 프로젝트 레드",
      "release_date": "2015-05-18",
      "genre": "액션 RPG",
      "price": 39900,
      "platforms": ["PC", "PS4", "Xbox One", "닌텐도 스위치"],
      "rating": 4.9,
      "description": "플레이어가 게롤트로 변신하여 어두운 판타지 세계에서 괴물을 사냥하는 방대한 RPG.",
      "image_url": "",
      "game_url": ""
    },
    {
      "title": "하데스",
      "developer": "슈퍼자이언트 게임즈",
      "release_date": "2020-09-17",
      "genre": "로그라이크",
      "price": 24900,
      "platforms": ["PC", "닌텐도 스위치", "PS5", "Xbox 시리즈 X"],
      "rating": 4.8,
      "description": "주인공 자그레우스가 지하 세계에서 탈출을 시도하는 던전 크롤러 로그라이크 게임.",
      "image_url": "",
      "game_url": ""
    }
  ]
}

'''
user_data = ""
library_data = ""
custom_prompt += f" 여기 우리가 가진 게임 정보가 있습니다: {game_data['data']}"
custom_prompt += f" 이건 사용자 데이터 입니다. {user_data['data']}"
custom_prompt += f" 사용자가 구매한 게임 데이터 입니다. {library_data['data']}"

#채팅 메시지를 저장할 세션 변수 생성
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 채팅 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 채팅 입력 필드 생성
# 페이지 하단에 자동으로 표시
if prompt := st.chat_input("무슨 일이신가요?"):

    # 현재 프롬프트를 저장하고 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # OpenAI API를 이용한 응답 생성
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": custom_prompt},  # 시스템 메시지로 프롬프트 엔지니어링 적용
            *[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
        ],
        stream=True,
    )

    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
