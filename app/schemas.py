from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    price: int

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    price: str  # 문자열로 저장되어 있음
    url: str | None = None

class Product(ProductBase):
    id: int
    
    class Config:
        from_attributes = True

class ProductCreate(ProductBase):
    pass

class ProductNameToModelRequest(BaseModel):
    product_name: str

class ProductNameToModelResponse(BaseModel):
    product_name: str
    model_name: str
    saved: bool
    message: str

class ProductNameToModelMappingsResponse(BaseModel):
    mappings: dict[str, str]
    total_count: int

