import streamlit as st
from openai import OpenAI
from fastapi import FastAPI
import random


# Show title and description.
st.title("💬 Chatbot")
st.write(
    "이건 gamefoge 사이트의 챗봇입니다. 모르는 것을 물어보고 원하는 답을 얻어보세요!"
    "오늘의 추천 게임, 공지사항, 문의사항 등 다 가능합니다."
    "재밌는 채팅하시고 gamefoge에서 관련 게임을 구매해보세요!"
)

#FastAPI인스턴스 생성
app = FastAPI()


# Create an OpenAI client.
client = OpenAI(api_key=st.secrets["openai_api_key"])

custom_prompt = "당신은 주어진 데이터를 바탕으로 유용하고 도움이되는 정확한 답변을 제공하는 유용한 어시스턴트입니다."
base_data = '''
{
"Notice": [
    {
    "도움말": "상점 탭에서 게임으로 들어가 장바구니 버튼을 누르면 게임 구매 가능"
    "문의처": "gameforge@gmail.com"
    "사이트 개발자": "윤명철, 신성용, 이인지, 박건후, 김민선"
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
custom_prompt += f" 여기 사전 정보가 있습니다: {base_data}"

# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message. This will display
# automatically at the bottom of the page.
if prompt := st.chat_input("무슨 일이신가요?"):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate a response using the OpenAI API.
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

    # Stream the response to the chat using `st.write_stream`, then store it in 
    # session state.
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
