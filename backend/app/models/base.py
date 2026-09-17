from sqlalchemy import Column, Integer, String, Float, Boolean, Date
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