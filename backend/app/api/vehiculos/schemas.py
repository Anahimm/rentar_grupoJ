from pydantic import BaseModel
from typing import Optional

class VehiculoBase(BaseModel):
    marca: str
    modelo: str
    anio: int
    color: Optional[str] = None
    tipo_vehiculo: str
    precio_diario: float

# Para crear, exigimos la patente
class VehiculoCreate(VehiculoBase):
    patente: str

# Al devolver datos, incluye el ID, estado y activo (generados por la BD)
class VehiculoResponse(VehiculoBase):
    id: int
    patente: str
    estado: str
    activo: bool

    class Config:
        from_attributes = True