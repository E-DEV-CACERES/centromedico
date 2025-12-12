"""
API FastAPI para Sistema de Centro Médico
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException as FastAPIHTTPException
from contextlib import asynccontextmanager
from app.routers import pacientes, doctor, citas, consultas, receta, historial, examenes, usuarios, auth
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

# Filtrar CancelledError en lifespan (son normales al cerrar el servidor)
class CancelledErrorFilter(logging.Filter):
    """Filtro para suprimir CancelledError en lifespan"""
    def filter(self, record):
        # No mostrar errores de CancelledError en el lifespan
        if "CancelledError" in str(record.getMessage()) and "lifespan" in str(record.getMessage()):
            return False
        return True

# Aplicar filtro a los loggers relevantes
for logger_name in ["uvicorn.error", "uvicorn", "starlette"]:
    logging.getLogger(logger_name).addFilter(CancelledErrorFilter())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan handler para manejar el inicio y cierre de la aplicación.
    Esto previene errores de CancelledError al cerrar el servidor.
    """
    # Startup
    logger.info("Iniciando aplicación...")
    try:
        # Verificar que la base de datos existe y es accesible
        import sqlite3
        from app.database import DATABASE_URL
        conn = sqlite3.connect(DATABASE_URL)
        conn.close()
        logger.info("Base de datos verificada correctamente")
    except Exception as e:
        logger.warning(f"Advertencia al verificar base de datos: {e}")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")
    # Dar tiempo para que las conexiones se cierren correctamente
    await asyncio.sleep(0.1)


app = FastAPI(
    title="Sistema de Centro Médico API",
    description="API REST para gestión de centro médico",
    version="1.0.0",
    lifespan=lifespan
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
        # Estas excepciones son normales durante el cierre del servidor
        # No las registramos como errores
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

