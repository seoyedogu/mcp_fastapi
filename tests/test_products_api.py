"""products API 테스트"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_products_list():
    """모든 상품 조회"""
    print("=" * 60)
    print("1. 모든 상품 조회 (처음 5개)")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/products?limit=5")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total items: {len(data)}")
    print("\n첫 번째 상품:")
    if data:
        print(json.dumps(data[0], indent=2, ensure_ascii=False))
    print()

def test_single_product():
    """단일 상품 조회"""
    print("=" * 60)
    print("2. 단일 상품 조회 (ID=1)")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/products/1")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print()

def test_search():
    """검색 기능"""
    print("=" * 60)
    print("3. 상품 검색 (키워드: RTX5060Ti)")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/products/search/RTX5060Ti")
    print(f"Status: {response.status_code}")
    print(f"검색 결과: {len(response.json())}개")
    for idx, product in enumerate(response.json()[:3], 1):
        print(f"\n{idx}. ID: {product['id']}")
        print(f"   이름: {product['name']}")
        print(f"   가격: {product['price']}")
    print()

def test_statistics():
    """통계 정보"""
    print("=" * 60)
    print("4. 통계 정보")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/products")
    all_products = response.json()
    
    print(f"전체 상품 수: {len(all_products)}개")
    if all_products:
        prices = [int(p['price']) for p in all_products if p['price'].isdigit()]
        if prices:
            print(f"최저가: {min(prices):,}원")
            print(f"최고가: {max(prices):,}원")
            print(f"평균가: {sum(prices)/len(prices):,.0f}원")
    print()

if __name__ == "__main__":
    try:
        test_products_list()
        test_single_product()
        test_search()
        test_statistics()
    except requests.exceptions.ConnectionError:
        print("❌ 서버가 실행되고 있지 않습니다.")
        print("먼저 'python -m uvicorn app.main:app --reload'를 실행하세요.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")


