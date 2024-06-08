import os
import time
import json
from openai import OpenAI
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 초기화
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key is missing. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI(api_key=api_key)

# 어시스턴트 ID 로드 또는 생성
assistant_key = os.environ.get("OPENAI_ASSISTANT_KEY")
if not assistant_key:
    assistant = client.beta.assistants.create(
        name="Language Learning Assistant",
        instructions=(
            "You are an assistant designed to help users learn new languages. "
            "When a user provides a summary of what they learned today, you will suggest the next topic for them to study. "
            "You also provide definitions and context for vocabulary words they want to learn more about."
        ),
        response_format={"type": "json"},
        tools=[{"type": "retrieval"}],
        model="gpt-4"
    )
    assistant_key = assistant.id
    print(f"New assistant created with ID: {assistant_key}")
else:
    print(f"Using existing assistant with ID: {assistant_key}")

# 스레드 ID 로드 또는 생성
thread_key = os.environ.get("OPENAI_THREAD_KEY")
if not thread_key:
    thread = client.beta.threads.create()
    thread_key = thread.id
    print(f"New thread created with ID: {thread_key}")
else:
    print(f"Using existing thread with ID: {thread_key}")

def get_learning_suggestion(content):
    # 메시지 추가
    message = client.beta.threads.messages.create(
        thread_id=thread_key,
        role="user",
        content=content
    )

    # 어시스턴트 실행
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_key,
        assistant_id=assistant_key,
        instructions='''
        Please output the information in structured JSON format without using markdown code blocks.
        Make the response like this:
        {"next_study_topic": "Your suggestion for the next topic to study", "explanation": "Explanation of the current topic"}
        '''
    )

    # 실행 결과 출력
    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread_key)
        for message in messages.data:
            result = message.content[0].text.value
            json_response = json.loads(result)
            print(json.dumps(json_response, indent=4, ensure_ascii=False))
    else:
        print(f"Run status: {run.status}")

def get_additional_vocabulary(word):
    # 메시지 추가
    message = client.beta.threads.messages.create(
        thread_id=thread_key,
        role="user",
        content=f"단어 '{word}'에 대해 추가 학습할 단어를 추천해 주세요."
    )

    # 어시스턴트 실행
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_key,
        assistant_id=assistant_key,
        instructions='''
        Please output the information in structured JSON format without using markdown code blocks.
        Make the response like this:
        {"related_words": ["word1", "word2", "word3"], "explanation": "Explanation of the provided word"}
        '''
    )

    # 실행 결과 출력
    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread_key)
        for message in messages.data:
            result = message.content[0].text.value
            json_response = json.loads(result)
            print(json.dumps(json_response, indent=4, ensure_ascii=False))
    else:
        print(f"Run status: {run.status}")

# 사용자 입력 받기
today_content = input("오늘 배운 내용을 입력하세요: ")
important_word = input("학습하고 싶은 중요한 단어를 입력하세요: ")

# 다음 학습 방향 제안
print("다음 학습할 내용:")
get_learning_suggestion(today_content)

# 추가 학습 단어 추천
print("추가 학습할 단어:")
get_additional_vocabulary(important_word)
