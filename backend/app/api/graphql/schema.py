import strawberry
from typing import Annotated, List, Optional
from datetime import date, datetime
from strawberry.types import Info
from app.core.database import SessionLocal
from app.models.base import Reserva, Vehiculo, Cliente
from app.services.reservas import a_hora_local, calcular_dias, vehiculo_disponible

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

    @strawberry.field(description="Busca vehículos disponibles aplicando filtros opcionales de características y fechas.")
    def consultar_disponibilidad(
        self,
        tipo_vehiculo: Annotated[Optional[str], strawberry.argument(description="Ej: SEDAN, SUV")] = None,
        marca: Annotated[Optional[str], strawberry.argument(description="Ej: Toyota")] = None,
        modelo: Annotated[Optional[str], strawberry.argument(description="Ej: Corolla")] = None,
        precio_maximo: Annotated[Optional[float], strawberry.argument(description="Precio máximo por día")] = None,
        fecha_desde: Annotated[Optional[datetime], strawberry.argument(description="Fecha de retiro del vehículo")] = None,
        fecha_hasta: Annotated[Optional[datetime], strawberry.argument(description="Fecha de devolución del vehículo")] = None
    ) -> List[VehiculoGraphQL]:
        
        db = SessionLocal()
        try:
            # Consulta base a la tabla real de Vehículos
            query = db.query(Vehiculo)

            # Aplicación de los filtros opcionales
            if tipo_vehiculo:
                query = query.filter(Vehiculo.tipo_vehiculo.ilike(tipo_vehiculo))
            if marca:
                query = query.filter(Vehiculo.marca.ilike(marca))
            if modelo:
                query = query.filter(Vehiculo.modelo.ilike(modelo))
            if precio_maximo:
                query = query.filter(Vehiculo.precio_diario <= precio_maximo)
                
            vehiculos_db = query.all()
            resultados = []
        
            # Mapeamos a VehiculoGraphQL y filtramos por fecha
            for v in vehiculos_db:
                # Si nos pasaron ambas fechas, verificamos la disponibilidad
                if fecha_desde and fecha_hasta:
                    # Si la función dice que NO está disponible, saltamos este vehículo
                    if not vehiculo_disponible(db, v.id, fecha_desde, fecha_hasta):
                        continue
                
                resultados.append(
                    VehiculoGraphQL(
                        patente=v.patente,
                        marca=v.marca,
                        modelo=v.modelo,
                        anio=v.anio,
                        color=v.color,
                        tipo_vehiculo=v.tipo_vehiculo,
                        precio_diario=v.precio_diario
                    )
                )

            return resultados
        finally:
            db.close()
            
    @strawberry.field(description="Consulta el historial de alquileres. Un CLIENTE solo ve el suyo")
    def historial_alquileres(self, cliente_id: int) -> List[HistorialAlquilerType]:
        db = SessionLocal()
        try:
            # Filtramos reservas del cliente con estado FINALIZADO o CANCELADA
            reservas = db.query(Reserva).filter(
                Reserva.cliente_id == cliente_id,
                Reserva.estado.in_(["FINALIZADO", "CANCELADA"])
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