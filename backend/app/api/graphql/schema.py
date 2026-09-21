import strawberry
from typing import Annotated, List, Optional
from datetime import date, datetime
from strawberry.types import Info
from app.core.database import SessionLocal
from app.models.base import Reserva, Vehiculo, Cliente
from app.services.reservas import a_hora_local, calcular_dias

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

@strawberry.type(description="Reserva de un vehículo realizada por un cliente")
class ReservaGraphQL:
    id: int = strawberry.field(description="Identificador de la reserva")
    cliente_id: int = strawberry.field(description="ID del cliente")
    cliente: str = strawberry.field(description="Nombre y apellido del cliente")
    vehiculo_id: int = strawberry.field(description="ID del vehículo")
    vehiculo: str = strawberry.field(description="Marca y modelo del vehículo")
    patente: str = strawberry.field(description="Patente del vehículo")
    tipo_vehiculo: Optional[str] = strawberry.field(description="SEDAN, SUV, PICKUP, COUPE o HATCHBACK")
    fecha_inicio: datetime = strawberry.field(description="Fecha y hora de inicio del alquiler")
    fecha_fin: datetime = strawberry.field(description="Fecha y hora de finalización del alquiler")
    dias: int = strawberry.field(description="Cantidad de días cobrados (por día iniciado)")
    precio_diario: float = strawberry.field(description="Precio diario al momento de reservar")
    importe_total: float = strawberry.field(description="Importe total de la reserva")
    estado: str = strawberry.field(description="CONFIRMADA o CANCELADA")


def leer_rol(info: Info):
    # El rol se simula con headers (el sistema no tiene login): X-Rol y X-Cliente-Id
    headers = info.context["request"].headers
    rol = (headers.get("x-rol") or "").upper()
    if rol not in ("ADMIN", "CLIENTE"):
        raise ValueError("Header X-Rol requerido: ADMIN o CLIENTE")
    cliente_id = headers.get("x-cliente-id")
    if rol == "CLIENTE":
        if not cliente_id or not cliente_id.isdigit():
            raise ValueError("Header X-Cliente-Id requerido para el rol CLIENTE")
        return rol, int(cliente_id)
    return rol, None


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

    @strawberry.field(description=(
        "Consulta de reservas con filtros opcionales. Requiere el header X-Rol (ADMIN o CLIENTE). "
        "El ADMIN ve las reservas de todos los clientes; un CLIENTE (header X-Cliente-Id) solo ve las suyas, "
        "aunque envíe otro clienteId."
    ))
    def reservas(
        self,
        info: Info,
        cliente_id: Annotated[Optional[int], strawberry.argument(description="Filtrar por cliente (solo ADMIN)")] = None,
        vehiculo_id: Annotated[Optional[int], strawberry.argument(description="Filtrar por vehículo")] = None,
        tipo_vehiculo: Annotated[Optional[str], strawberry.argument(description="Filtrar por tipo de vehículo")] = None,
        estado: Annotated[Optional[str], strawberry.argument(description="CONFIRMADA o CANCELADA")] = None,
        fecha_desde: Annotated[Optional[datetime], strawberry.argument(description="Reservas cuyo período termina después de esta fecha")] = None,
        fecha_hasta: Annotated[Optional[datetime], strawberry.argument(description="Reservas cuyo período empieza antes de esta fecha")] = None,
    ) -> List[ReservaGraphQL]:
        rol, cliente_actual = leer_rol(info)
        if rol == "CLIENTE":
            cliente_id = cliente_actual

        db = SessionLocal()
        try:
            query = db.query(Reserva).join(Vehiculo).join(Cliente)
            if cliente_id is not None:
                query = query.filter(Reserva.cliente_id == cliente_id)
            if vehiculo_id is not None:
                query = query.filter(Reserva.vehiculo_id == vehiculo_id)
            if tipo_vehiculo:
                query = query.filter(Vehiculo.tipo_vehiculo == tipo_vehiculo)
            if estado:
                query = query.filter(Reserva.estado == estado)
            # Rango de fechas: reservas cuyo período se cruza con [fecha_desde, fecha_hasta]
            if fecha_desde:
                query = query.filter(Reserva.fecha_fin > a_hora_local(fecha_desde))
            if fecha_hasta:
                query = query.filter(Reserva.fecha_inicio < a_hora_local(fecha_hasta))

            return [
                ReservaGraphQL(
                    id=r.id,
                    cliente_id=r.cliente_id,
                    cliente=f"{r.cliente.nombre} {r.cliente.apellido}",
                    vehiculo_id=r.vehiculo_id,
                    vehiculo=f"{r.vehiculo.marca} {r.vehiculo.modelo}",
                    patente=r.vehiculo.patente,
                    tipo_vehiculo=r.vehiculo.tipo_vehiculo,
                    fecha_inicio=r.fecha_inicio,
                    fecha_fin=r.fecha_fin,
                    dias=calcular_dias(r.fecha_inicio, r.fecha_fin),
                    precio_diario=r.precio_diario,
                    importe_total=r.importe_total,
                    estado=r.estado,
                )
                for r in query.order_by(Reserva.fecha_inicio.desc()).all()
            ]
        finally:
            db.close()

schema = strawberry.Schema(query=Query)