from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 기존 데이터베이스에 연결 (SQLite 예시)
# 절대 경로는 sqlite:///로 시작해야 함. Windows 경로는 슬래시로 변환
SQLALCHEMY_DATABASE_URL = "sqlite:///C:/Users/home/Desktop/sw/mcp_project/data.sqlite"

# SQLite는 기본적으로 동일 스레드만 허용 → FastAPI 개발 서버에서 편하게 쓰려면 False
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# FastAPI 의존성 주입용 세션
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
