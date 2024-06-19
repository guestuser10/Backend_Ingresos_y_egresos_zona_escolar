from pydantic import BaseModel

class SupBase(BaseModel):
    id: int 
    username: str
    password: str
    rol: str
    name: str
    estado: str


class SupUpdate(BaseModel):
    username: str
    password: str
    name: str
    estado: str