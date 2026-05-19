from google import genai
from datetime import datetime
from dotenv import load_dotenv
import os
import json
import time
# API KEY
load_dotenv()
SYSTEM_PROMPT = """

Bạn là trợ lý AI tiếng Việt thân thiện và thông minh.

Quy tắc:

- Trả lời rõ ràng
- Không bịa thông tin
- Nếu không chắc thì nói không chắc
- Trả lời tự nhiên như con người
- Ưu tiên tiếng Việt
- Ghi nhớ thông tin quan trọng của người dùng
- Giải thích dễ hiểu

"""
client = genai.Client(api_key=os.getenv(
        "GEMINI_API_KEY"
    ))


print("=== CHATBOT GEMINI MEMORY ===")
print("Gõ 'exit' để thoát\n")

# Biến lưu lịch sử hội thoại
try:

    with open(
        "memory/short_memory.json",
        "r",
        encoding="utf8"
    ) as f:

        chat_history = json.load(f)
    with open(
        "memory/long_memory.json",
        "r",
        encoding="utf8"
    ) as f:

        long_memory = json.load(f)

except:

    chat_history = []
    long_memory = []

while True:
    question = input("Bạn: ")
    important_keywords = [
        "tên tôi là",
        "tôi tên là",
        "tôi thích",
        "rất thích",
        "mục tiêu của tôi",
        "tôi đang học",
        "sở thích của tôi"
    ]

    for keyword in important_keywords:

        if keyword in question.lower():

            long_memory.append(question)

            with open(
                "memory/long_memory.json",
                "w",
                encoding="utf8"
            ) as f:

                json.dump(
                    long_memory,
                    f,
                    ensure_ascii=False
            )
    # Thoát
    if question.lower() == "exit":
        print("Chatbot: Tạm biệt!")
        break

    # Lấy thời gian hiện tại
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Lưu câu hỏi người dùng
    chat_history.append(f"Người dùng: {question}")

    # Ghép toàn bộ lịch sử chat
    MAX_HISTORY = 10

    recent_history = chat_history[-MAX_HISTORY:]

    full_conversation = "\n".join(
        recent_history
    )

    # Prompt gửi AI
    prompt = f"""

    {SYSTEM_PROMPT}

    Hôm nay là:

    {current_time}
    Thông tin quan trọng về người dùng:

    {long_memory}

    Lịch sử cuộc trò chuyện:

    {full_conversation}

    Hãy trả lời tin nhắn mới nhất của người dùng.

    """

    try:

        response = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=prompt
        )

        answer = ""

        print("Gemini: ", end="")

        for chunk in response:

            if chunk.text:

                print(chunk.text, end="", flush=True)

                answer += chunk.text

        print()

    except Exception as e:

        answer = f"Có lỗi xảy ra: {e}"

    # In ra màn hình theo kiểu streaming

    print("Gemini: ", end="")

    for char in answer:

        print(
            char,
            end="",
            flush=True
        )

        time.sleep(0.02)

    print()

    # Lưu câu trả lời vào lịch sử
    chat_history.append(f"Gemini: {answer}")
    