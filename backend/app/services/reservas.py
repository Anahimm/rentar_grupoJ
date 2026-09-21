import math
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.base import Reserva

ESTADO_CONFIRMADA = "CONFIRMADA"
ESTADO_CANCELADA = "CANCELADA"


def a_hora_local(fecha: datetime) -> datetime:
    # Si llega una fecha con zona horaria se pasa a hora local sin zona, para compararla con datetime.now()
    if fecha.tzinfo is not None:
        return fecha.astimezone().replace(tzinfo=None)
    return fecha


def filtro_solapamiento(query, desde: datetime, hasta: datetime):
    # Dos períodos se cruzan si uno empieza antes de que termine el otro y viceversa.
    # Una reserva que termina justo cuando empieza otra NO se considera cruce.
    return query.filter(Reserva.fecha_inicio < hasta, Reserva.fecha_fin > desde)


def vehiculo_disponible(
    db: Session,
    vehiculo_id: int,
    desde: datetime,
    hasta: datetime,
) -> bool:
    # Solo las reservas CONFIRMADAS ocupan el vehículo (las CANCELADAS lo liberan)
    query = db.query(Reserva).filter(
        Reserva.vehiculo_id == vehiculo_id,
        Reserva.estado == ESTADO_CONFIRMADA,
    )
    return filtro_solapamiento(query, desde, hasta).first() is None


def calcular_dias(desde: datetime, hasta: datetime) -> int:
    # Se cobra por día iniciado: 25 horas = 2 días. Mínimo 1 día.
    horas = (hasta - desde).total_seconds() / 3600
    return max(1, math.ceil(horas / 24))


def calcular_importe(desde: datetime, hasta: datetime, precio_diario: float) -> float:
    return round(calcular_dias(desde, hasta) * precio_diario, 2)
