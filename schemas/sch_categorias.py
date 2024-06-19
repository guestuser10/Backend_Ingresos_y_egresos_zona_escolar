from pydantic import BaseModel
from typing import Optional


#Tabla Categoria y SubCategoria
class CategoriaBase(BaseModel):
    nombre: str
    identificador: str
    escuela_nombre: str

class CategoriaCrear(CategoriaBase):

    pass

class CategoriaUpdate(CategoriaBase):

    nombre: str
    identificador: str 


