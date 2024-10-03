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

@app.get("/test")
async def test():
    return {
        "id": random.randint(1,10), #지정한 범위 안에서 랜덤한 수를 되돌려 준다
        "name": "name",
        "address": "Tokyo",
        "age": 30
        }

@app.get('/text')
def test(request):
    return {'test':'text'}


# Create an OpenAI client.
client = OpenAI(api_key=st.secrets["openai_api_key"])

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
if prompt := st.chat_input("What is up?"):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate a response using the OpenAI API.
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ],
        stream=True,
    )

    # Stream the response to the chat using `st.write_stream`, then store it in 
    # session state.
    with st.chat_message("assistant"):
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
