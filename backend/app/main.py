from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.core.database import engine, Base
from app.models import base
from app.api.vehiculos import router as vehiculos_router
from app.api.graphql.schema import schema

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Rentar - Grupo J",
    description="Sistema de gestión de alquileres de vehículos",
    version="1.0.0"
)

# CONFIGURACIÓN CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Permiso para el front
    allow_credentials=True,
    allow_methods=["*"], # Permite POST, GET, PUT, DELETE
    allow_headers=["*"],
)

# RUTAS REST
app.include_router(vehiculos_router.router)

# RUTA GRAPHQL
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def read_root():
    return {"mensaje": "API Rentar funcionando. Entrá a /docs para ver el Swagger."}