"""데이터베이스 연결 테스트 스크립트"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """데이터베이스 연결 상태 확인"""
    print("=" * 50)
    print("1. 데이터베이스 연결 상태 확인")
    print("=" * 50)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_db_info():
    """데이터베이스 정보 확인"""
    print("=" * 50)
    print("2. 데이터베이스 정보 확인")
    print("=" * 50)
    response = requests.get(f"{BASE_URL}/db-info")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_items():
    """아이템 조회"""
    print("=" * 50)
    print("3. 아이템 조회")
    print("=" * 50)
    response = requests.get(f"{BASE_URL}/items")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_create_item():
    """아이템 생성"""
    print("=" * 50)
    print("4. 아이템 생성 테스트")
    print("=" * 50)
    item_data = {
        "name": "테스트 아이템",
        "price": 1000
    }
    response = requests.post(f"{BASE_URL}/items", json=item_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

if __name__ == "__main__":
    try:
        test_health()
        test_db_info()
        test_items()
        test_create_item()
    except requests.exceptions.ConnectionError:
        print("서버가 실행되고 있지 않습니다. 먼저 'uvicorn app.main:app --reload'를 실행하세요.")
    except Exception as e:
        print(f"오류 발생: {e}")

