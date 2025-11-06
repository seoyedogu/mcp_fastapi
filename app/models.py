from sqlalchemy import Column, Integer, String, Text
from .db import Base

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    price = Column(Integer, nullable=False)

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False, unique=True)  # 중복 방지
    price = Column(Text, nullable=False)  # 문자열로 저장되어 있음
    url = Column(Text, nullable=True)

