from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.base import Vehiculo
from app.api.vehiculos import schemas

# Agrupamos las rutas con /vehiculos
router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])

@router.post("/", response_model=schemas.VehiculoResponse)
def crear_vehiculo(vehiculo: schemas.VehiculoCreate, db: Session = Depends(get_db)):
    # Verificamos que la patente no exista para no duplicar autos
    db_vehiculo = db.query(Vehiculo).filter(Vehiculo.patente == vehiculo.patente).first()
    if db_vehiculo:
        raise HTTPException(status_code=400, detail="La patente ya está registrada")
    
    # Guardado en base de datos (estado DISPONIBLE por defecto)
    nuevo_vehiculo = Vehiculo(**vehiculo.model_dump())
    db.add(nuevo_vehiculo)
    db.commit()
    db.refresh(nuevo_vehiculo)
    return nuevo_vehiculo

@router.get("/", response_model=List[schemas.VehiculoResponse])
def listar_vehiculos(db: Session = Depends(get_db)):
    # Devuelve todos los vehículos cargados
    return db.query(Vehiculo).all()