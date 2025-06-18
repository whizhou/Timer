import requests
import time

BASE_URL = "http://127.0.0.1:5000"

def test_independent_requests():
    # 第一次请求（会创建会话文件）
    response1 = requests.post(
        f"{BASE_URL}/chat", 
        data={'message': 'First message'}
    )
    print("Response 1:", response1.json())
    
    # 获取会话ID（从响应Cookie或服务端日志获取）
    session_id = response1.cookies.get('session')
    print(f"Session ID: {session_id}")
    
    # 第二次请求（模拟独立请求，不带Cookie）
    response2 = requests.post(
        f"{BASE_URL}/chat",
        data={'message': 'Second message'}
    )
    print("Response 2:", response2.json())
    
    # 第三次请求（手动携带之前的会话ID）
    response3 = requests.post(
        f"{BASE_URL}/chat",
        data={'message': 'Third message'},
        cookies={'session': session_id} if session_id else None  # 手动传递会话ID
    )
    print("Response 3:", response3.json())
    print(f"Session ID from Response 3: {response3.cookies.get('session')}")

def test_pet_routes():
    for i in range(3):
        response = requests.get(
            f"{BASE_URL}/schedule/titles/{i}",
        )
        print(f"Response for schedule/titles/{i}:\n", response.json())

        response = requests.get(
            f"{BASE_URL}/schedule/quantity/{i}",
        )
        print(f"Response for schedule/quantity/{i}:\n", response.json())

if __name__ == "__main__":
    # test_independent_requests()

    test_pet_routes()