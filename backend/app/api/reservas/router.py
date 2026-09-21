from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.base import Cliente, Reserva, Vehiculo
from app.api.reservas import schemas
from app.services.reservas import (
    ESTADO_CANCELADA,
    ESTADO_CONFIRMADA,
    a_hora_local,
    calcular_importe,
    vehiculo_disponible,
)

router = APIRouter(prefix="/reservas", tags=["Reservas"])


def obtener_reserva(db: Session, reserva_id: int) -> Reserva:
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if not reserva:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada")
    return reserva


def validar_acceso_cliente(reserva: Reserva, rol: Optional[str], cliente_id: Optional[int]):
    # Un CLIENTE solo puede operar sobre sus propias reservas
    if rol and rol.upper() == "CLIENTE" and reserva.cliente_id != cliente_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="La reserva no pertenece al cliente")


# 1. ALTA DE RESERVA
@router.post(
    "/",
    response_model=schemas.ReservaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una reserva",
    description=(
        "Registra una reserva en estado CONFIRMADA. Verifica que el cliente y el vehículo existan y estén activos, "
        "que la fecha de inicio sea futura, que la de finalización sea posterior y que el vehículo no tenga otra "
        "reserva CONFIRMADA que se superponga. El importe se calcula por día iniciado x precio diario."
    ),
    responses={
        400: {"description": "Cliente o vehículo inactivo, o fechas inválidas"},
        404: {"description": "Cliente o vehículo inexistente"},
        409: {"description": "El vehículo ya está reservado en ese período"},
    },
)
def crear_reserva(datos: schemas.ReservaCreate, db: Session = Depends(get_db)):
    fecha_inicio = a_hora_local(datos.fecha_inicio)
    fecha_fin = a_hora_local(datos.fecha_fin)

    cliente = db.query(Cliente).filter(Cliente.id == datos.cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El cliente no existe")
    if not cliente.activo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El cliente está inactivo")

    vehiculo = db.query(Vehiculo).filter(Vehiculo.id == datos.vehiculo_id).first()
    if not vehiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El vehículo no existe")
    if not vehiculo.activo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El vehículo está inactivo")

    if fecha_inicio <= datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La fecha de inicio debe ser futura")
    if fecha_fin <= fecha_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de finalización debe ser posterior a la de inicio",
        )

    if not vehiculo_disponible(db, vehiculo.id, fecha_inicio, fecha_fin):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El vehículo ya tiene una reserva en ese período",
        )

    nueva_reserva = Reserva(
        cliente_id=cliente.id,
        vehiculo_id=vehiculo.id,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        precio_diario=vehiculo.precio_diario,
        importe_total=calcular_importe(fecha_inicio, fecha_fin, vehiculo.precio_diario),
        estado=ESTADO_CONFIRMADA,
    )
    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)
    return nueva_reserva


# 2. CONSULTA (POR ID)
@router.get(
    "/{reserva_id}",
    response_model=schemas.ReservaResponse,
    summary="Obtener una reserva",
    responses={404: {"description": "Reserva no encontrada"}},
)
def obtener_una_reserva(reserva_id: int, db: Session = Depends(get_db)):
    return obtener_reserva(db, reserva_id)


# 3. CANCELACIÓN (la reserva no se elimina, solo cambia de estado)
@router.patch(
    "/{reserva_id}/cancelar",
    response_model=schemas.ReservaResponse,
    summary="Cancelar una reserva",
    description=(
        "Cambia el estado de la reserva a CANCELADA sin eliminarla. Solo se permite si la reserva está CONFIRMADA "
        "y su período todavía no comenzó. Si se envía el header X-Rol: CLIENTE, la reserva debe pertenecer al "
        "cliente indicado en X-Cliente-Id."
    ),
    responses={
        400: {"description": "La reserva ya fue cancelada o el período ya comenzó"},
        403: {"description": "La reserva no pertenece al cliente"},
        404: {"description": "Reserva no encontrada"},
    },
)
def cancelar_reserva(
    reserva_id: int,
    x_rol: Optional[str] = Header(default=None, description="ADMIN o CLIENTE"),
    x_cliente_id: Optional[int] = Header(default=None, description="ID del cliente que opera (si X-Rol es CLIENTE)"),
    db: Session = Depends(get_db),
):
    reserva = obtener_reserva(db, reserva_id)
    validar_acceso_cliente(reserva, x_rol, x_cliente_id)

    if reserva.estado != ESTADO_CONFIRMADA:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La reserva ya se encuentra cancelada")
    if reserva.fecha_inicio <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cancelar: el período de alquiler ya comenzó",
        )

    reserva.estado = ESTADO_CANCELADA
    db.commit()
    db.refresh(reserva)
    return reserva
