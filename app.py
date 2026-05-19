import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from datetime import datetime
import json
import time
from tavily import TavilyClient
import html

load_dotenv()

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

TAVILY_API_KEY = os.getenv(
    "TAVILY_API_KEY"
)

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
# Lúc này model bạn dùng sẽ là: model="llama3-8b-8192"

tavily = TavilyClient(
    api_key=TAVILY_API_KEY
)

def search_web(query):

    result = tavily.search(
        query=query,
        search_depth="basic",
        max_results=3
    )

    return result
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🤖",
    layout="wide"
)


light_css = """
<style>

.stApp {
    background-color: white;
}

section[data-testid="stSidebar"] {

    background-color: #ede9fe;

    border-right: 1px solid #ddd6fe;
}

.main-title {

    color: #111827;
}

.subtitle {

    color: #6b7280;
}

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-user"]
) {

    display: flex;

    justify-content: flex-end;

    width: 100%;
}

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-user"]
) > div {

    background-color: #ede9fe;

    border: 1px solid #ddd6fe;

    border-radius: 18px;

    padding: 14px 18px;

    max-width: 75%;

    width: fit-content;
}

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-assistant"]
) {

    background-color: white;

    border: 1px solid #e5e7eb;

    border-radius: 18px;

    padding: 16px;

    margin-bottom: 14px;

    margin-right: 120px;

    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    max-width: 75%;
    width: fit-content;
}

textarea {

    background-color: white !important;

    color: #111827 !important;

    border-radius: 24px !important;

    border: 1px solid #d1d5db !important;

    padding: 14px 18px !important;

    font-size: 16px !important;

    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
}

.stButton button {

    background: #8b5cf6;

    color: white;

    border-radius: 12px;
}
[data-testid="stChatMessage"] {

    width: fit-content;

    max-width: 75%;
}

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-user"]
) [data-testid="stChatMessageContent"] {

    text-align: left;
}

[data-testid="stChatMessage"] {

    display: flex;
}

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-user"]
) {

    justify-content: flex-end;
}

.user-row {

    display: flex;

    justify-content: flex-end;

    margin-bottom: 18px;
}

.user-bubble {

    background: #ede9fe;

    color: #111827;

    padding: 14px 18px;

    border-radius: 18px;

    max-width: 70%;

    font-size: 16px;

    line-height: 1.6;
}

.assistant-row {

    display: flex;

    justify-content: flex-start;

    margin-bottom: 18px;
}

.assistant-bubble {

    background: white;

    border: 1px solid #e5e7eb;

    padding: 14px 18px;

    border-radius: 18px;

    max-width: 70%;

    font-size: 16px;

    line-height: 1.6;
}
</style>
"""

st.markdown(
    light_css,
    unsafe_allow_html=True
)

st.markdown("""
<style>

/* toàn bộ chat message */
[data-testid="stChatMessage"]{
    display:flex;
    align-items:flex-start;
    width:100%;
}

/* USER MESSAGE */
[data-testid="stChatMessage"]:has(
[data-testid="chatAvatarIcon-user"]
){
    flex-direction:row-reverse;
    justify-content:flex-start;
    text-align:right;
}

/* assistant giữ bên trái */
[data-testid="stChatMessage"]:has(
[data-testid="chatAvatarIcon-assistant"]
){
    flex-direction:row;
}

/* bubble user */
[data-testid="stChatMessage"]:has(
[data-testid="chatAvatarIcon-user"]
) .stMarkdown{
    background:#ede9fe;
    padding:12px 16px;
    border-radius:18px;
    max-width:500px;
}

/* bubble assistant */
[data-testid="stChatMessage"]:has(
[data-testid="chatAvatarIcon-assistant"]
) .stMarkdown{
    background:#f3f4f6;
    padding:12px 16px;
    border-radius:18px;
    max-width:500px;
}

</style>
""", unsafe_allow_html=True)

with st.sidebar:

    st.title("AI Assistant")

    st.markdown("---")

    if st.button("➕ Đoạn chat mới"):
        # 🌟 TRƯỚC KHI XÓA: Lưu lại đoạn chat hiện tại vào lịch sử
        if "messages" in st.session_state and len(st.session_state.messages) > 0:
            
            # Tìm câu hỏi đầu tiên của user để làm Tiêu đề (Title)
            chat_title = "Cuộc trò chuyện mới"
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    chat_title = msg["content"]
                    break
            
            # Khởi tạo bộ nhớ lịch sử nếu chưa có
            if "past_conversations" not in st.session_state:
                st.session_state.past_conversations = []
            
            # Lưu toàn bộ tin nhắn hiện tại vào kho lưu trữ
            st.session_state.past_conversations.append({
                "title": chat_title,
                "messages": st.session_state.messages.copy() # Phải dùng .copy()
            })

        # SAU ĐÓ MỚI XÓA KHUNG CHAT HIỆN TẠI
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    st.subheader("📜 Lịch sử trò chuyện")

    # Đảm bảo biến được khởi tạo
    if "past_conversations" not in st.session_state:
        st.session_state.past_conversations = []

    # 1. Hiển thị các cuộc trò chuyện CŨ ĐÃ LƯU (đảo ngược để cái mới nhất lên trên)
    for i, conv in enumerate(reversed(st.session_state.past_conversations)):
        title = conv["title"]
        short_title = title[:35] + "..." if len(title) > 35 else title
        # Dùng st.button để giao diện giống một menu có thể click (mặc dù hiện tại chưa gắn chức năng click)
        st.markdown(f"🗄️ **{short_title}**")

    # 2. Hiển thị cuộc trò chuyện HIỆN TẠI ĐANG CHAT
    if "messages" in st.session_state:
        current_user_msgs = [msg["content"] for msg in st.session_state.messages if msg["role"] == "user"]
        if current_user_msgs:
            curr_title = current_user_msgs[0]
            short_curr = curr_title[:35] + "..." if len(curr_title) > 35 else curr_title
            st.markdown(f"🟢 *{short_curr}*")
            
    # Nếu trống trơn thì báo không có
    if len(st.session_state.past_conversations) == 0 and ("messages" not in st.session_state or len(st.session_state.messages) == 0):
        st.caption("Không có cuộc trò chuyện nào.")   
    

st.markdown(
    '<div class="main-title">🤖 AI Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Chatbot AI thông minh có memory và internet realtime</div>',
    unsafe_allow_html=True
)

try:
    with open(
        "memory/short_memory.json",
        "r",
        encoding="utf8"
    ) as f:

        short_memory = json.load(f)

    with open(
        "memory/long_memory.json",
        "r",
        encoding="utf8"
    ) as f:

        long_memory = json.load(f)

    with open(
        "memory/smart_memory.json",
        "r",
        encoding="utf8"
    ) as f:

        smart_memory = json.load(f)
    with open( 
        "memory/chat_history.json", 
        "r", 
        encoding="utf8" 
    ) as f: 
        chat_history = json.load(f)

except:

    short_memory = []
    long_memory = []
    smart_memory = {}
    chat_history = []
if "messages" not in st.session_state:

    st.session_state.messages = []

for message in st.session_state.messages:

    if message["role"] == "user":
        st.markdown(
            f'<div style="display:flex; justify-content:flex-end; margin:10px 0;"><div style="background:#ede9fe; padding:12px 16px; border-radius:18px; max-width:70%; text-align:left;">\n\n{message["content"]}\n\n</div></div>',
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            f'<div style="display:flex; justify-content:flex-start; margin:10px 0;"><div style="background:#f3f4f6; padding:12px 16px; border-radius:18px; max-width:70%; text-align:left;">\n\n{message["content"]}\n\n</div></div>',
            unsafe_allow_html=True
        )


user_message = st.chat_input("Nhập tin nhắn...")
if user_message:

    lower_msg = user_message.lower()

    if "tên tôi là" in lower_msg:

        smart_memory["name"] = user_message.split("là")[-1].strip()

    if "tôi tên là" in lower_msg:

        smart_memory["name"] = user_message.split("là")[-1].strip()

    if "tôi" in lower_msg and "tuổi" in lower_msg:

        smart_memory["age"] = user_message

    if "tôi làm" in lower_msg:

        smart_memory["job"] = user_message.split("làm")[-1].strip()

    if "tôi sống ở" in lower_msg:

        smart_memory["location"] = user_message.split("ở")[-1].strip()

    if "mục tiêu của tôi" in lower_msg:

        smart_memory["goal"] = user_message.split("là")[-1].strip()

    if "tôi thích" in lower_msg:

        hobby = user_message.split("thích")[-1].strip()

        if hobby not in smart_memory["hobbies"]:

            smart_memory["hobbies"].append(hobby)

    if "thói quen của tôi" in lower_msg:

        habit = user_message.split("là")[-1].strip()

        if habit not in smart_memory["habits"]:

            smart_memory["habits"].append(habit)


if user_message:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    st.session_state.pending_prompt = user_message

    st.rerun()


if "pending_prompt" in st.session_state:
    user_message = st.session_state.pending_prompt
    del st.session_state.pending_prompt

    # 🌟 1. Tạo danh sách tin nhắn gửi đi (Bắt đầu bằng System Prompt)
    api_messages = [
        {
            "role": "system", 
            "content": (
                "Bạn là một AI chatbot trợ lý thông minh và thân thiện. "
                "HÃY TUÂN THỦ NGHIÊM NGẶT 2 QUY TẮC SAU:\n"
                "1. CHỈ sử dụng tiếng Việt chuẩn 100%, tuyệt đối không tự ý chèn từ ngữ của ngôn ngữ khác (Hàn, Trung, Anh...).\n"
                "2. Đọc kỹ lịch sử trò chuyện để nắm bắt thông tin. Tuyệt đối KHÔNG ĐƯỢC HỎI LẠI những thông tin mà người dùng đã cung cấp hoặc những gì bạn vừa tự nhắc tới ở đoạn trên."
            )
        }
    ]

    # 🌟 2. Đưa TOÀN BỘ lịch sử chat hiện tại vào payload (đã bao gồm câu hỏi mới nhất của user)
    for msg in st.session_state.messages:
        api_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # 🌟 3. Gọi API với danh sách tin nhắn đầy đủ
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=api_messages, # Thay vì chỉ gửi prompt, ta gửi cả mảng api_messages
        max_tokens=2048,
        stream=True
    )

    full_response = ""
    
    # Sử dụng khối st.chat_message chuẩn để bọc luồng hiển thị
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)

    # 🌟 BƯỚC 2: THÊM ĐOẠN NÀY ĐỂ LƯU KẾT QUẢ CỦA AI VÀO LỊCH SỬ CHAT
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response
        }
    )

    # Sau khi đã append đầy đủ cả User lẫn Assistant vào st.session_state.messages mới rerun
    st.rerun()