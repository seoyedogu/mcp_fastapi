"""크롤링 API 테스트 스크립트"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_crawl():
    """크롤링 API 테스트"""
    print("=" * 60)
    print("크롤링 API 테스트")
    print("=" * 60)
    
    # 테스트할 키워드
    keyword = "노트북"
    max_items = 10
    
    print(f"\n키워드: {keyword}")
    print(f"최대 크롤링 수: {max_items}")
    print("\n크롤링 시작...")
    
    # 크롤링 요청
    payload = {
        "keyword": keyword,
        "max_items": max_items
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/crawl",
            json=payload,
            timeout=30  # 크롤링은 시간이 걸릴 수 있음
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ 크롤링 성공!")
            print(f"검색 키워드: {result['keyword']}")
            print(f"발견된 상품 수: {result['total_found']}개")
            print(f"새로 저장된 상품: {result['new_items']}개")
            print(f"중복된 상품: {result['duplicate_items']}개")
            
            print("\n크롤링된 상품 목록 (처음 5개):")
            for idx, item in enumerate(result['items'][:5], 1):
                print(f"\n{idx}. {item['name'][:50]}...")
                print(f"   가격: {item['price']}원")
                print(f"   URL: {item['url'][:80]}...")
            
            return result  # 결과 반환
        else:
            print(f"\n❌ 오류 발생: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("\n⏱️ 요청 시간 초과 (크롤링이 너무 오래 걸림)")
        return None
    except requests.exceptions.ConnectionError:
        print("\n❌ 서버에 연결할 수 없습니다.")
        print("서버가 실행 중인지 확인하세요: python -m uvicorn app.main:app --reload")
        return None
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        return None

def test_view_crawled_products():
    """크롤링된 상품 조회 (DB에서 확인)"""
    print("\n" + "=" * 60)
    print("크롤링된 상품 조회 (DB에서 최근 5개)")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/products?limit=5")
        if response.status_code == 200:
            products = response.json()
            print(f"\n총 {len(products)}개의 상품:")
            if products:
                for idx, product in enumerate(products, 1):
                    print(f"\n{idx}. ID: {product['id']}")
                    print(f"   이름: {product['name'][:50]}...")
                    print(f"   가격: {product['price']}원")
                    if product.get('url'):
                        print(f"   URL: {product['url'][:60]}...")
            else:
                print("\n저장된 상품이 없습니다.")
    except Exception as e:
        print(f"오류: {e}")

def test_verify_db_storage(crawl_result):
    """크롤링 결과가 DB에 저장되었는지 확인"""
    print("\n" + "=" * 60)
    print("DB 저장 확인")
    print("=" * 60)
    
    if not crawl_result.get('success'):
        print("크롤링이 실패했습니다.")
        return
    
    keyword = crawl_result.get('keyword', '')
    new_items = crawl_result.get('new_items', 0)
    
    try:
        # 크롤링한 키워드로 검색
        response = requests.get(f"{BASE_URL}/products/search/{keyword}")
        if response.status_code == 200:
            products = response.json()
            print(f"\n키워드 '{keyword}'로 검색한 결과: {len(products)}개")
            print(f"크롤링에서 새로 저장된 상품: {new_items}개")
            
            if products:
                print("\n저장된 상품 샘플 (처음 3개):")
                for idx, product in enumerate(products[:3], 1):
                    print(f"\n{idx}. ID: {product['id']}")
                    print(f"   이름: {product['name'][:50]}...")
                    print(f"   가격: {product['price']}원")
            else:
                print("\n⚠️ DB에 저장된 상품이 없습니다.")
        else:
            print(f"검색 오류: {response.status_code}")
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    print("크롤링 API 테스트를 시작합니다...\n")
    
    # 크롤링 실행
    crawl_result = test_crawl()
    
    # DB 저장 확인
    if crawl_result:
        test_verify_db_storage(crawl_result)
    
    # 최근 상품 조회
    test_view_crawled_products()
    
    print("\n테스트 완료!")

