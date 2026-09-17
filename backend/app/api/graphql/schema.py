import strawberry
from typing import List, Optional

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

schema = strawberry.Schema(query=Query)