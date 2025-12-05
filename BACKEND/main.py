"""
API FastAPI para Sistema de Centro Médico
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException as FastAPIHTTPException
from app.routers import pacientes, doctor, citas, consultas, facturacion, receta, historial, examenes, usuarios, auth
from sqlite3 import OperationalError, DatabaseError
import logging
import traceback
import asyncio

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurar logging de uvicorn para ver menos ruido
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

app = FastAPI(
    title="Sistema de Centro Médico API",
    description="API REST para gestión de centro médico",
    version="1.0.0"
)

# Configurar CORS - Debe estar antes de incluir los routers
# Nota: No se puede usar "*" en allow_origins cuando allow_credentials=True
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server (puerto por defecto)
        "http://localhost:5174",  # Puerto alternativo de Vite
        "http://localhost:3000",  # Alternativa
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para capturar todas las excepciones no manejadas"""
    # Excluir excepciones del sistema que no deben ser manejadas
    # No manejar excepciones del sistema de asyncio o del framework
    if isinstance(exc, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)):
        # Re-lanzar estas excepciones para que el sistema las maneje correctamente
        raise
    
    # No manejar HTTPException de FastAPI (ya están manejadas)
    if isinstance(exc, FastAPIHTTPException):
        raise
    
    logger.error(
        f"Error no manejado: {str(exc)}\n"
        f"Path: {request.url.path}\n"
        f"Method: {request.method}\n"
        f"Traceback: {traceback.format_exc()}",
        exc_info=True
    )
    
    # Manejar errores específicos de base de datos
    if isinstance(exc, OperationalError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Error de base de datos",
                "detail": str(exc),
                "message": "No se pudo acceder a la base de datos. Verifica que la base de datos existe y está accesible."
            }
        )
    
    if isinstance(exc, DatabaseError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Error de base de datos",
                "detail": str(exc),
                "message": "Error al procesar la consulta a la base de datos."
            }
        )
    
    # Error genérico
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Error interno del servidor",
            "detail": str(exc),
            "message": "Ocurrió un error inesperado. Por favor, contacta al administrador."
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para errores de validación de Pydantic"""
    logger.warning(f"Error de validación: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Error de validación",
            "detail": exc.errors(),
            "message": "Los datos proporcionados no son válidos. Verifica el formato de la solicitud."
        }
    )


@app.get("/api/health")
async def health_check():
    """Endpoint de salud que verifica la conexión a la base de datos"""
    try:
        import sqlite3
        from app.database import DATABASE_URL
        
        # Verificar conexión a la base de datos
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        
        return {
            "status": "ok",
            "message": "API funcionando correctamente",
            "database": "conectada"
        }
    except Exception as e:
        logger.error(f"Error en health check: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "message": "API funcionando pero base de datos no disponible",
                "database": "desconectada",
                "error": str(e)
            }
        )

