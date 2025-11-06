# FastAPI 제품명 정규화 API

FastAPI와 SQLAlchemy를 사용하여 제품명을 모델명으로 자동 변환하는 API입니다. 다나와에서 제품을 검색하여 모델명을 자동으로 추출하고, 메모리에 저장하여 재사용할 수 있습니다.

## 주요 기능

- 📦 **제품명 정규화**: 제품 이름을 입력하면 다나와에서 검색하여 모델명으로 자동 변환
- 💾 **메모리 저장**: 변환된 제품명-모델명 매핑을 메모리에 저장하여 재사용
- 🔍 **자동 검색**: 하드코딩 없이 다양한 제품명에 대해 자동으로 모델명 추출

## 설치

```bash
pip install -r requirements.txt
```

## 실행

```bash
# test 디렉토리로 이동
cd test

# 방법 1: uvicorn으로 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 방법 2: 모듈로 실행
python -m uvicorn app.main:app --reload

# 방법 3: 직접 실행
python -m app.main
```

## API 엔드포인트

### 일반
- `GET /` - 루트 엔드포인트
- `GET /health` - 데이터베이스 연결 상태 확인
- `GET /db-info` - 데이터베이스 정보 및 테이블 목록

### Items (테스트 테이블)
- `GET /items` - 모든 아이템 조회 (페이징 지원: skip, limit)
- `GET /items/{item_id}` - 특정 아이템 조회
- `POST /items` - 새 아이템 생성
- `DELETE /items/{item_id}` - 아이템 삭제

### Products (실제 상품 데이터)
- `GET /products` - 모든 상품 조회 (페이징 지원: skip, limit)
- `GET /products/{product_id}` - 특정 상품 조회
- `GET /products/search/{keyword}` - 상품명으로 검색

### 제품명 정규화
- `POST /normalize-product-name` - 제품명을 모델명으로 변환하고 저장
- `GET /normalize-product-name/mappings` - 저장된 모든 제품명-모델명 매핑 조회

## 사용 예시

### 제품명 정규화

제품명을 모델명으로 변환하는 엔드포인트입니다. 다나와에서 제품을 검색하여 모델명을 자동으로 추출합니다.

#### Windows PowerShell:
```powershell
curl -X POST http://localhost:8000/normalize-product-name -H "Content-Type: application/json" -d '{\"product_name\": \"삼성 블루스카이 5500\"}'
```

#### Windows CMD:
```cmd
curl -X POST http://localhost:8000/normalize-product-name -H "Content-Type: application/json" -d "{\"product_name\": \"삼성 블루스카이 5500\"}"
```

#### Git Bash / Linux / Mac:
```bash
curl -X POST http://localhost:8000/normalize-product-name \
  -H "Content-Type: application/json" \
  -d '{"product_name": "삼성 블루스카이 5500"}'
```

**응답 예시:**
```json
{
  "product_name": "삼성 블루스카이 5500",
  "model_name": "AX060CG500G",
  "saved": true,
  "message": "제품명 '삼성 블루스카이 5500'이 모델명 'AX060CG500G'으로 저장되었습니다."
```

### 저장된 매핑 조회

메모리에 저장된 모든 제품명-모델명 매핑을 조회합니다.

```bash
curl http://localhost:8000/normalize-product-name/mappings
```

**응답 예시:**
```json
{
  "mappings": {
    "삼성 블루스카이 5500": "AX060CG500G",
    "LG 그램 17인치": "17Z90R-K.AA56K1"
  },
  "total_count": 2
}
```

### Products 조회

```bash
# 모든 상품 조회 (처음 5개)
curl http://localhost:8000/products?limit=5

# 특정 상품 조회
curl http://localhost:8000/products/1

# 상품 검색
curl http://localhost:8000/products/search/라이젠

# 브라우저에서 확인
# http://localhost:8000/products
```

### API 테스트

```bash
# 테스트 스크립트 실행 (tests 폴더에서)
cd tests
python test_products_api.py
python test_connection.py

# 또는 test 폴더에서 직접 실행
python tests/test_products_api.py
python tests/test_connection.py
```

## 동작 원리

1. **제품명 입력**: 사용자가 제품명을 입력합니다.
2. **캐시 확인**: 이미 저장된 매핑이 있는지 확인합니다.
3. **다나와 검색**: 캐시에 없으면 다나와에서 제품을 검색합니다.
4. **모델명 추출**: 제품 상세 페이지에서 모델명을 추출합니다.
   - 스펙 테이블에서 "모델명" 항목 찾기
   - 제품명에서 대문자+숫자 패턴 추출 (예: AX060CG500G)
   - 제품 상세 정보에서 패턴 추출
5. **메모리 저장**: 찾은 모델명을 메모리에 저장하여 다음 요청 시 재사용합니다.

## 데이터베이스 설정

`app/db.py` 파일에서 데이터베이스 연결 설정을 변경할 수 있습니다:

```python
# SQLite (기본값)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# PostgreSQL 예시
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"

# MySQL 예시  
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"
```

## 문서

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 주의사항

- 제품명-모델명 매핑은 메모리에 저장되므로 서버를 재시작하면 초기화됩니다.
- 다나와에서 모델명을 찾지 못할 경우 404 오류가 반환됩니다.
- 네트워크 오류 또는 다나와 페이지 구조 변경 시 모델명 추출이 실패할 수 있습니다.

## 향후 개발 계획

- 데이터베이스에 매핑 정보 영구 저장
- 크롤링 기능과 연동하여 저장된 모델명으로 크롤링 수행
- 모델명 추출 로직 개선 및 정확도 향상
