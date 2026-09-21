from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id = Column(Integer, primary_key=True, index=True)
    patente = Column(String, unique=True, index=True, nullable=False)
    marca = Column(String, nullable=False)
    modelo = Column(String, nullable=False)
    anio = Column(Integer, nullable=False)
    color = Column(String)
    tipo_vehiculo = Column(String)
    precio_diario = Column(Float, nullable=False)
    estado = Column(String, default="DISPONIBLE") 
    activo = Column(Boolean, default=True)

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    documento = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    telefono = Column(String)
    fecha_nacimiento = Column(Date)
    activo = Column(Boolean, default=True)

class Reserva(Base):
    __tablename__ = "reservas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    vehiculo_id = Column(Integer, ForeignKey("vehiculos.id"), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    # Se guarda el precio del momento de la reserva para que el importe no cambie si se actualiza el vehículo
    precio_diario = Column(Float, nullable=False)
    importe_total = Column(Float, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    estado = Column(String, default="CONFIRMADA") # CONFIRMADA, CANCELADA

    cliente = relationship("Cliente")
    vehiculo = relationship("Vehiculo")