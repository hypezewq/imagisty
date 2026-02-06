from pydantic import BaseModel

class AutoPart(BaseModel):
    id: int
    title: str
    price: int
    category: str