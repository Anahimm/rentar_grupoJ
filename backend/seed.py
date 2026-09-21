"""Carga datos de prueba en rentar.db. Uso (desde la carpeta backend): python seed.py

Se puede ejecutar varias veces: no duplica vehículos, clientes ni reservas ya cargados.
Las reservas se insertan directo en la base (sin pasar por la API) para poder crear
algunas con fechas pasadas y así probar la cancelación de una reserva ya iniciada.
"""
from datetime import datetime, timedelta

from app.core.database import Base, SessionLocal, engine
from app.models.base import Cliente, Reserva, Vehiculo
from app.services.reservas import calcular_importe

VEHICULOS = [
    dict(patente="AB123CD", marca="Toyota", modelo="Corolla", anio=2022, color="Blanco", tipo_vehiculo="SEDAN", precio_diario=15000),
    dict(patente="EF456GH", marca="Ford", modelo="Ranger", anio=2023, color="Gris", tipo_vehiculo="PICKUP", precio_diario=25000),
    dict(patente="IJ789KL", marca="Toyota", modelo="Yaris", anio=2021, color="Rojo", tipo_vehiculo="HATCHBACK", precio_diario=12000),
    dict(patente="MN012OP", marca="Jeep", modelo="Compass", anio=2024, color="Negro", tipo_vehiculo="SUV", precio_diario=30000),
    dict(patente="QR345ST", marca="Ford", modelo="Mustang", anio=2020, color="Azul", tipo_vehiculo="COUPE", precio_diario=40000),
    dict(patente="UV678WX", marca="Fiat", modelo="Cronos", anio=2019, color="Blanco", tipo_vehiculo="SEDAN", precio_diario=10000, activo=False),
]

CLIENTES = [
    dict(documento="30111222", nombre="Ana", apellido="Pérez", email="ana@mail.com", telefono="1155551111"),
    dict(documento="31222333", nombre="Bruno", apellido="Gómez", email="bruno@mail.com", telefono="1155552222"),
    dict(documento="32333444", nombre="Carla", apellido="López", email="carla@mail.com"),
    dict(documento="33444555", nombre="Diego", apellido="Martínez", email="diego@mail.com", activo=False),
]

# (documento del cliente, patente, días desde hoy al inicio, duración en días, estado)
RESERVAS = [
    ("30111222", "AB123CD", 3, 4, "CONFIRMADA"),   # futura: se puede cancelar
    ("30111222", "EF456GH", 10, 2, "CANCELADA"),
    ("30111222", "IJ789KL", -2, 5, "CONFIRMADA"),  # ya empezó: NO se puede cancelar
    ("31222333", "MN012OP", 5, 3, "CONFIRMADA"),
    ("31222333", "AB123CD", 15, 2, "CONFIRMADA"),
    ("32333444", "QR345ST", 7, 1, "CONFIRMADA"),
]


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for datos in VEHICULOS:
            if not db.query(Vehiculo).filter(Vehiculo.patente == datos["patente"]).first():
                db.add(Vehiculo(**datos))
        for datos in CLIENTES:
            if not db.query(Cliente).filter(Cliente.documento == datos["documento"]).first():
                db.add(Cliente(**datos))
        db.commit()

        if db.query(Reserva).count() == 0:
            hoy = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
            for documento, patente, desde, duracion, estado in RESERVAS:
                cliente = db.query(Cliente).filter(Cliente.documento == documento).one()
                vehiculo = db.query(Vehiculo).filter(Vehiculo.patente == patente).one()
                inicio = hoy + timedelta(days=desde)
                fin = inicio + timedelta(days=duracion)
                db.add(Reserva(
                    cliente_id=cliente.id,
                    vehiculo_id=vehiculo.id,
                    fecha_inicio=inicio,
                    fecha_fin=fin,
                    precio_diario=vehiculo.precio_diario,
                    importe_total=calcular_importe(inicio, fin, vehiculo.precio_diario),
                    estado=estado,
                ))
            db.commit()

        print(f"Vehículos: {db.query(Vehiculo).count()} | Clientes: {db.query(Cliente).count()} | Reservas: {db.query(Reserva).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
