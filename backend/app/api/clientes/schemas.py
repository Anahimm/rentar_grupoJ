from pydantic import BaseModel
from typing import Optional
from datetime import date

# Esquema base con campos comunes
class ClienteBase(BaseModel):
    nombre: str
    apellido: str
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[date] = None

# Para la creación (POST): documento y email obligatorios
class ClienteCreate(ClienteBase):
    documento: str
    email: str

# Para actualización (PUT): campos opcionales
class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[date] = None

# Respuesta de la API
class ClienteResponse(ClienteBase):
    id: int
    documento: str
    email: str
    activo: bool

    class Config:
        from_attributes = True