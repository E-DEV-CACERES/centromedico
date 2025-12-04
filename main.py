"""
API FastAPI para Sistema de Centro Médico
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import pacientes, doctor, citas, consultas, facturacion, receta, historial, examenes, usuarios

app = FastAPI(
    title="Sistema de Centro Médico API",
    description="API REST para gestión de centro médico",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(pacientes.router, prefix="/api/pacientes", tags=["Pacientes"])
app.include_router(doctor.router, prefix="/api/doctores", tags=["Doctores"])
app.include_router(citas.router, prefix="/api/citas", tags=["Citas"])
app.include_router(consultas.router, prefix="/api/consultas", tags=["Consultas"])
app.include_router(facturacion.router, prefix="/api/facturacion", tags=["Facturación"])
app.include_router(receta.router, prefix="/api/recetas", tags=["Recetas"])
app.include_router(historial.router, prefix="/api/historial", tags=["Historial Médico"])
app.include_router(examenes.router, prefix="/api/examenes", tags=["Exámenes de Laboratorio"])
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios del Sistema"])


@app.get("/")
async def root():
    return {
        "message": "API del Sistema de Centro Médico",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "API funcionando correctamente"}

