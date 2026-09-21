import strawberry
from typing import List, Optional
from datetime import date
from app.core.database import SessionLocal
from app.models.base import Reserva, Vehiculo, Cliente

# Estructura de datos que GraphQL le va a devolver al Frontend
@strawberry.type
class VehiculoGraphQL:
    patente: str
    marca: str
    modelo: str
    anio: int
    color: Optional[str]
    tipo_vehiculo: str
    precio_diario: float


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
    def ping(self) -> str:
        return "GraphQL configurado y funcionando"

    @strawberry.field
    def consultar_disponibilidad(
        self,
        tipo_vehiculo: Optional[str] = None,
        marca: Optional[str] = None,
        modelo: Optional[str] = None,
        precio_maximo: Optional[float] = None
        # Las fechas se agregan cuando se armen las reservas
    ) -> List[VehiculoGraphQL]:
        
        # Mocking de datos para testear
        mock_db = [
            VehiculoGraphQL(patente="AB123CD", marca="Toyota", modelo="Corolla", anio=2022, color="Blanco", tipo_vehiculo="SEDAN", precio_diario=15000),
            VehiculoGraphQL(patente="EF456GH", marca="Ford", modelo="Ranger", anio=2023, color="Gris", tipo_vehiculo="PICKUP", precio_diario=25000),
            VehiculoGraphQL(patente="IJ789KL", marca="Toyota", modelo="Yaris", anio=2021, color="Rojo", tipo_vehiculo="HATCHBACK", precio_diario=12000)
        ]

        # Aplicación de los filtros opcionales
        resultados = mock_db
        if tipo_vehiculo:
            resultados = [v for v in resultados if v.tipo_vehiculo == tipo_vehiculo]
        if marca:
            resultados = [v for v in resultados if v.marca == marca]
        if modelo:
            resultados = [v for v in resultados if v.modelo == modelo]
        if precio_maximo:
            resultados = [v for v in resultados if v.precio_diario <= precio_maximo]

        return resultados
    
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