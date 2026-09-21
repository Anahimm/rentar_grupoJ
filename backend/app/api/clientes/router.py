from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.base import Cliente
from app.api.clientes import schemas

router = APIRouter(prefix="/clientes", tags=["Clientes"])

# 1. ALTA DE CLIENTE
@router.post("/", response_model=schemas.ClienteResponse, status_code=status.HTTP_201_CREATED)
def crear_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    # Validar que el documento sea único
    if db.query(Cliente).filter(Cliente.documento == cliente.documento).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Ya existe un cliente registrado con ese documento"
        )
    
    # Validar que el email sea único
    if db.query(Cliente).filter(Cliente.email == cliente.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Ya existe un cliente registrado con ese email"
        )
    
    nuevo_cliente = Cliente(**cliente.model_dump())
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    return nuevo_cliente

# 2. CONSULTA (LISTAR TODOS)
@router.get("/", response_model=List[schemas.ClienteResponse])
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(Cliente).all()

# 3. CONSULTA (POR ID)
@router.get("/{cliente_id}", response_model=schemas.ClienteResponse)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return cliente

# 4. MODIFICACIÓN
@router.put("/{cliente_id}", response_model=schemas.ClienteResponse)
def actualizar_cliente(cliente_id: int, datos: schemas.ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    
    # Si quiere cambiar el email, validar que no pertenezca a otro cliente
    if datos.email and datos.email != cliente.email:
        email_ocupado = db.query(Cliente).filter(Cliente.email == datos.email, Cliente.id != cliente_id).first()
        if email_ocupado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="El email ya pertenece a otro cliente"
            )

    # Actualizamos solo los campos que fueron enviados
    datos_actualizados = datos.model_dump(exclude_unset=True)
    for clave, valor in datos_actualizados.items():
        setattr(cliente, clave, valor)

    db.commit()
    db.refresh(cliente)
    return cliente

# 5. BAJA LÓGICA
@router.delete("/{cliente_id}", response_model=schemas.ClienteResponse)
def baja_logica_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    
    cliente.activo = False
    db.commit()
    db.refresh(cliente)
    return cliente