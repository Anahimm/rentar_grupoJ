from pydantic import BaseModel, Field
from datetime import datetime


# Para el alta (POST)
class ReservaCreate(BaseModel):
    cliente_id: int = Field(description="ID del cliente que realiza la reserva")
    vehiculo_id: int = Field(description="ID del vehículo a reservar")
    fecha_inicio: datetime = Field(description="Fecha y hora de inicio (debe ser futura)", examples=["2026-12-01T10:00:00"])
    fecha_fin: datetime = Field(description="Fecha y hora de finalización (posterior al inicio)", examples=["2026-12-05T10:00:00"])


# Respuesta de la API
class ReservaResponse(BaseModel):
    id: int
    cliente_id: int
    vehiculo_id: int
    fecha_inicio: datetime
    fecha_fin: datetime
    precio_diario: float = Field(description="Precio diario del vehículo al momento de reservar")
    importe_total: float = Field(description="Cantidad de días (por día iniciado) x precio diario")
    estado: str = Field(description="CONFIRMADA o CANCELADA")

    class Config:
        from_attributes = True
