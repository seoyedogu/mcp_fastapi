from fastapi import FastAPI, HTTPException
from . import schemas

app = FastAPI(title="My API")

# 제품명 -> 모델명 매핑 저장용 변수 (메모리에 저장)
product_name_to_model: dict[str, str] = {}

@app.get("/")
def read_root():
    return {"msg": "hello, fastapi"}

# 제품명을 모델명으로 변환하는 엔드포인트
@app.post("/normalize-product-name", response_model=schemas.ProductNameToModelResponse)
def normalize_product_name(request: schemas.ProductNameToModelRequest):
    """
    제품 이름을 모델명으로 정규화
    
    사용자가 제품 이름을 입력하면 모델명으로 변환하여 저장합니다.
    변환된 매핑은 메모리에 저장되며, 나중에 크롤링할 때 사용됩니다.
    
    Args:
        request: ProductNameToModelRequest (product_name: 제품 이름)
    
    Returns:
        ProductNameToModelResponse: 변환된 모델명 및 저장된 매핑 정보
    """
    if not request.product_name or not request.product_name.strip():
        raise HTTPException(status_code=400, detail="제품 이름을 입력해주세요.")
    
    product_name = request.product_name.strip()
    
    # 제품명을 모델명으로 변환하는 로직
    # 예: "삼성 블루스카이 5500" -> "AX060CG500G"
    model_name = convert_product_name_to_model(product_name)
    
    if not model_name:
        raise HTTPException(
            status_code=404,
            detail=f"제품명 '{product_name}'에 대한 모델명을 찾을 수 없습니다."
        )
    
    # 메모리에 저장 (key: 제품명, value: 모델명)
    product_name_to_model[product_name] = model_name
    
    return {
        "product_name": product_name,
        "model_name": model_name,
        "saved": True,
        "message": f"제품명 '{product_name}'이 모델명 '{model_name}'으로 저장되었습니다."
    }

@app.get("/normalize-product-name/mappings", response_model=schemas.ProductNameToModelMappingsResponse)
def get_product_name_mappings():
    """
    저장된 제품명-모델명 매핑 조회
    
    현재 메모리에 저장된 모든 제품명-모델명 매핑을 반환합니다.
    
    Returns:
        ProductNameToModelMappingsResponse: 저장된 모든 매핑 정보
    """
    return {
        "mappings": product_name_to_model,
        "total_count": len(product_name_to_model)
    }

def convert_product_name_to_model(product_name: str) -> str | None:
    """
    제품 이름을 모델명으로 변환하는 함수 (다나와에서 자동 검색)
    
    다나와에서 제품명으로 검색하여 첫 번째 결과의 모델명을 추출합니다.
    이미 저장된 매핑이 있으면 그것을 우선적으로 사용합니다.
    
    Args:
        product_name: 제품 이름 (예: "삼성 블루스카이 5500")
    
    Returns:
        모델명 (예: "AX060CG500G") 또는 None
    """
    import requests
    from bs4 import BeautifulSoup
    import urllib.parse
    import re
    
    # 먼저 저장된 매핑에서 확인 (캐시된 결과 우선 사용)
    if product_name in product_name_to_model:
        return product_name_to_model[product_name]
    
    # 대소문자 무시로 저장된 매핑 확인
    for key, value in product_name_to_model.items():
        if key.lower() == product_name.lower():
            return value
    
    # 다나와에서 검색하여 모델명 추출
    try:
        encoded_keyword = urllib.parse.quote(product_name)
        search_url = f"https://search.danawa.com/dsearch.php?query={encoded_keyword}&tab=main"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 첫 번째 제품의 링크 찾기
        first_product = soup.select_one(".product_list > .prod_item")
        if not first_product:
            return None
        
        # 제품 상세 페이지 링크 추출
        product_link_tag = first_product.select_one(".prod_name a") or first_product.select_one("a[class^='click_log_product_standard_title_']")
        if not product_link_tag or not product_link_tag.get("href"):
            return None
        
        product_url = product_link_tag["href"]
        if product_url.startswith("/info"):
            product_url = "http://prod.danawa.com" + product_url
        
        # 제품 상세 페이지에서 모델명 추출
        detail_response = requests.get(product_url, headers=headers, timeout=10)
        if detail_response.status_code != 200:
            return None
        
        detail_soup = BeautifulSoup(detail_response.text, "html.parser")
        
        # 모델명 추출 방법 1: 스펙 테이블에서 찾기
        model_name = None
        
        # "모델명" 또는 "제품모델명" 키워드로 찾기
        spec_rows = detail_soup.select("table.spec_tbl tr, .spec_tbl tr, .prod_spec tr")
        for row in spec_rows:
            th = row.select_one("th")
            td = row.select_one("td")
            if th and td:
                label = th.get_text(strip=True).lower()
                value = td.get_text(strip=True)
                
                if any(keyword in label for keyword in ["모델명", "제품모델명", "model", "model name"]):
                    model_name = value
                    break
        
        # 모델명 추출 방법 2: 제품명에서 패턴 추출 (예: 대문자+숫자 조합)
        if not model_name:
            product_title = detail_soup.select_one("h3.prod_tit, h1.prod_tit, .prod_tit")
            if product_title:
                title_text = product_title.get_text()
                # 모델명 패턴: 대문자+숫자 조합 (예: AX060CG500G, ABC123XYZ)
                pattern = r'\b[A-Z]{2,}[0-9A-Z]{4,}\b'
                matches = re.findall(pattern, title_text)
                if matches:
                    model_name = matches[0]
        
        # 모델명 추출 방법 3: 제품 상세 정보에서 추출
        if not model_name:
            detail_info = detail_soup.select_one(".prod_summary_info, .product_info")
            if detail_info:
                info_text = detail_info.get_text()
                pattern = r'\b[A-Z]{2,}[0-9A-Z]{4,}\b'
                matches = re.findall(pattern, info_text)
                if matches:
                    model_name = matches[0]
        
        return model_name if model_name else None
        
    except Exception as e:
        # 오류 발생 시 None 반환 (로그는 나중에 추가 가능)
        return None

# 직접 실행 가능하도록 설정
if __name__ == "__main__":
    import sys
    import os
    # 상대 임포트를 사용하기 위해 상위 디렉토리를 sys.path에 추가
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
