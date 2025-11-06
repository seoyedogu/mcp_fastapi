"""다나와 크롤러 모듈 - FastAPI에서 사용하기 위한 래퍼"""
import requests
from bs4 import BeautifulSoup
import urllib.parse
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy import delete
from . import models

def clear_products_table(db: Session):
    """
    products 테이블의 모든 데이터 삭제 (DB 초기화)
    
    Args:
        db: SQLAlchemy 세션
    """
    try:
        db.execute(delete(models.Product))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

def save_item(db: Session, name: str, price: str, url: str) -> bool:
    """
    DB에 저장 (SQLAlchemy ORM 사용)
    DB가 크롤링 시작 시 초기화되므로 중복 체크는 간단히 처리
    
    Args:
        db: SQLAlchemy 세션
        name: 제품명
        price: 가격
        url: 제품 URL
    
    Returns:
        bool: True면 저장 성공, False면 저장 실패
    """
    # 새 제품 저장
    new_product = models.Product(name=name, price=price, url=url)
    db.add(new_product)
    try:
        db.commit()
        db.refresh(new_product)
        return True  # 저장 성공
    except Exception as e:
        db.rollback()
        # UNIQUE 제약조건 위반 등으로 실패할 수 있음 (같은 크롤링 내에서 중복)
        return False

def crawl_danawa_by_keyword(db: Session, keyword: str, max_items: int = 50) -> Dict:
    """
    제품 키워드로 다나와 크롤링 및 DB 저장
    
    주의: 크롤링 시작 시 기존 products 테이블의 모든 데이터가 삭제됩니다.
    
    Args:
        db: SQLAlchemy 세션 (DB 저장용)
        keyword: 검색할 제품 키워드
        max_items: 최대 크롤링할 상품 수
    
    Returns:
        {
            "success": bool,
            "keyword": str,
            "total_found": int,
            "new_items": int,
            "duplicate_items": int,
            "items": List[Dict],
            "error": str | None
        }
    """
    # URL 인코딩
    encoded_keyword = urllib.parse.quote(keyword)
    search_url = f"https://search.danawa.com/dsearch.php?query={encoded_keyword}&tab=main"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
    }
    
    result = {
        "success": False,
        "keyword": keyword,
        "total_found": 0,
        "new_items": 0,
        "duplicate_items": 0,
        "items": [],
        "error": None
    }
    
    try:
        # DB 초기화: 기존 products 테이블의 모든 데이터 삭제
        clear_products_table(db)
        
        # HTTP 요청
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            result["error"] = f"HTTP 상태 코드: {response.status_code}"
            return result
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, "html.parser")
        product_list = soup.select(".product_list > .prod_item")
        
        if not product_list:
            result["error"] = "제품 목록을 찾을 수 없습니다. (선택자 오류 or 페이지 구조 변경)"
            return result
        
        result["total_found"] = len(product_list)
        
        # 각 제품 처리
        for idx, div in enumerate(product_list[:max_items]):
            try:
                # 제품명 추출
                name_tag = div.select_one(".prod_name a")
                if not name_tag:
                    name_tag = div.select_one("a[class^='click_log_product_standard_title_']")
                
                # 가격 추출
                price_tag = (
                    div.select_one(".price_sect strong.prc_t")
                    or div.select_one(".price_sect strong")
                    or div.select_one(".price_sect em")
                )
                
                name = name_tag.text.strip() if name_tag else "이름 없음"
                url_part = name_tag["href"] if name_tag and name_tag.has_attr("href") else ""
                url = (
                    "http://prod.danawa.com/" + url_part
                    if url_part.startswith("/info")
                    else url_part
                )
                price = (
                    price_tag.text.strip().replace(",", "").replace("원", "").strip()
                    if price_tag
                    else "가격 정보 없음"
                )
                
                # 유효한 데이터인지 확인
                if name != "이름 없음" and "가격 정보 없음" not in price and url:
                    # DB에 저장 (SQLAlchemy ORM 사용)
                    saved = save_item(db, name, price, url)
                    
                    item_data = {
                        "name": name,
                        "price": price,
                        "url": url
                    }
                    result["items"].append(item_data)
                    
                    if saved:
                        result["new_items"] += 1
                    else:
                        # 같은 크롤링 세션 내에서 중복된 경우
                        result["duplicate_items"] += 1
                
            except Exception as e:
                continue  # 개별 아이템 오류는 무시하고 계속
        
        result["success"] = True
        
    except requests.exceptions.RequestException as e:
        result["error"] = f"요청 오류: {str(e)}"
    except Exception as e:
        result["error"] = f"크롤링 오류: {str(e)}"
    
    return result

