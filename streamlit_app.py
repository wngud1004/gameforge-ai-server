import streamlit as st
from openai import OpenAI
from fastapi import FastAPI
import requests
import json
import random
import logging

# https://gameforge-ai-server.streamlit.app/?token=YOUR_ACCESS_TOKEN
st.title("💬 GameForge Chatbot")

# https://ludorium.store/api/user/login
user_info_url = "https://ludorium.store/api/user/mypage"
user_library_url = "https://ludorium.store/api/user/library/list"
game_list_url = "https://ludorium.store/api/user/game/0/list"
custom_prompt = "당신은 주어진 데이터를 바탕으로 유용하고 도움이되는 정확한 답변을 제공하는 게임 어시스턴트입니다."

# FastAPI 사용
app = FastAPI()

# OpenAPI key 가져오기
client = OpenAI(api_key=st.secrets["openai_api_key"])

# 로그 메시지 전송 함수
def log_message(message):
    logging.basicConfig(level=logging.DEBUG)  # 로그 레벨 설정 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    logging.info(message)

query_params = st.experimental_get_query_params()
auth_token = query_params.get("token", [None])[0]  # 'token' 매개변수를 가져옴

if auth_token:
    st.session_state.auth_token = auth_token  # 인증 토큰을 세션 상태에 저장
    log_message("인증 토큰이 성공적으로 받아졌습니다. " + auth_token)

    headers = {
        "Authorization": f"Bearer {auth_token}"  # Bearer 방식으로 Access Token 전달
    }

    # 사용자 정보 GET 요청
    response = requests.get(user_info_url, headers=headers, verify=False)

    if response.status_code == 200:
        user_data = response.json()
        print("사용자 정보:")
        print(f"이메일: {user_data['data']['email']}, 
              닉네임: {user_data['data']['nickname']}, 
              이름: {user_data['data']['name']}, 
              가입 날짜: {user_data['data']['regDate']}, 
              보상 포인트: {user_data['data']['rewardPoints']}")
        user_data = user_data['data']
    else:
        print(f"사용자 정보 API 요청에 실패했습니다. 상태 코드: {response.status_code}")
        user_data = "현재 사용자 데이터를 불러오는 것에 실패함"

    # 사용자 구매 게임 요청
    user_library_response = requests.get(user_library_url, headers=headers, verify=False)

    if user_library_response.status_code == 200:
        library_data = user_library_response.json()
        
        # 사용자 구매 게임 목록 출력
        print("구매 목록:")
        print(library_data['data'])
        library_data = library_data['data']
    else:
        library_data = "현재 사용자가 구매한 게임 정보를 불러오는 것에 실패함"


    # 전체 게임 목록
    game_list_response = requests.get(game_list_url, headers=headers, verify=False)

    if game_list_response.status_code == 200:
        game_data = game_list_response.json()
        
        # 전체 게임 목록 출력
        print("게임 목록 :")
        print(game_data['data'])
        game_data = game_data['data']
    else:
        game_data = "게임 목록을 불러오는 것에 실패함"

else:
    log_message("인증 토큰을 찾을 수 없습니다.")
    user_data = "현재 사용자가 로그인하기 전 상태라 사용자 정보 없음"
    library_data = "현재 사용자가 로그인하기 전 상태라 구매한 게임 정보 없음"
    game_data = "사이트에 게임 목록 없음"


custom_prompt += f" 여기 우리가 가진 게임 정보가 있습니다: {game_data}"
custom_prompt += f" 이건 사용자 데이터 입니다. {user_data}"
custom_prompt += f" 사용자가 구매한 게임 데이터 입니다. {library_data}"

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
