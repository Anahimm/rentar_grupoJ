import strawberry
from typing import List, Optional
from datetime import date
from app.core.database import SessionLocal
from app.models.base import Reserva, Vehiculo, Cliente

@strawberry.type
class HistorialAlquilerType:
    id: int
    vehiculo_marca: str
    vehiculo_modelo: str
    vehiculo_patente: str
    fecha_inicio: date
    fecha_fin: date
    estado: str
    dias: int
    importe: float

@strawberry.type
class Query:
    @strawberry.field
    def historial_alquileres(self, cliente_id: int) -> List[HistorialAlquilerType]:
        db = SessionLocal()
        try:
            # Filtramos reservas del cliente con estado FINALIZADO o CANCELADO
            reservas = db.query(Reserva).filter(
                Reserva.cliente_id == cliente_id,
                Reserva.estado.in_(["FINALIZADO", "CANCELADO"])
            ).all()

            resultado = []
            for r in reservas:
                # Calculamos los días de alquiler (mínimo 1 día)
                cant_dias = (r.fecha_fin - r.fecha_inicio).days
                if cant_dias <= 0:
                    cant_dias = 1
                
                # Obtenemos el precio diario del vehículo asociado
                precio = r.vehiculo.precio_diario if r.vehiculo else 0.0
                importe_total = round(cant_dias * precio, 2)

                resultado.append(
                    HistorialAlquilerType(
                        id=r.id,
                        vehiculo_marca=r.vehiculo.marca if r.vehiculo else "N/A",
                        vehiculo_modelo=r.vehiculo.modelo if r.vehiculo else "N/A",
                        vehiculo_patente=r.vehiculo.patente if r.vehiculo else "N/A",
                        fecha_inicio=r.fecha_inicio,
                        fecha_fin=r.fecha_fin,
                        estado=r.estado,
                        dias=cant_dias,
                        importe=importe_total
                    )
                )
            return resultado
        finally:
            db.close()

schema = strawberry.Schema(query=Query)