"""
Router para autenticación de usuarios
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlite3 import Connection
from typing import Dict, Any
from app.database import get_db
from pydantic import BaseModel
import logging
import secrets

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

router = APIRouter()


class LoginRequest(BaseModel):
    Usuario: str
    Contrasena: str


class LoginResponse(BaseModel):
    usuario: Dict[str, Any]
    token: str


def row_to_dict(row) -> Dict[str, Any]:
    """Convierte un Row de SQLite a un diccionario"""
    if row is None:
        return None
    result = {}
    for key in row.keys():
        value = row[key]
        result[key] = value
    return result


def verificar_tabla_usuarios(cursor):
    """Verifica si la tabla usuarios_sistema existe, si no, la crea"""
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='usuarios_sistema'
    """)
    if not cursor.fetchone():
        logger.warning("La tabla usuarios_sistema no existe. Creándola...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios_sistema (
                Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                Usuario TEXT NOT NULL UNIQUE,
                Contrasena TEXT NOT NULL,
                Codigo_Doctor INTEGER,
                Rol TEXT DEFAULT 'Recepcionista',
                Activo INTEGER DEFAULT 1,
                Ultimo_Acceso DATETIME,
                Fecha_Creacion DATETIME,
                Fecha_Modificacion DATETIME,
                FOREIGN KEY (Codigo_Doctor) REFERENCES doctor(Codigo)
            )
        """)


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(credentials: LoginRequest, db: Connection = Depends(get_db)):
    """
    Autenticar un usuario del sistema
    
    - Verifica que el usuario existe y está activo
    - Valida la contraseña
    - Retorna el usuario (sin contraseña) y un token de sesión
    """
    try:
        cursor = db.cursor()
        
        # Verificar y crear tabla si no existe
        verificar_tabla_usuarios(cursor)
        db.commit()
        
        # Buscar usuario por nombre de usuario
        cursor.execute(
            "SELECT * FROM usuarios_sistema WHERE Usuario = ? AND Activo = 1",
            (credentials.Usuario,)
        )
        usuario = cursor.fetchone()
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos"
            )
        
        usuario_dict = row_to_dict(usuario)
        
        # Verificar contraseña
        #  NOTA: En producción, usar bcrypt para comparar contraseñas hasheadas
        # from passlib.context import CryptContext
        # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # if not pwd_context.verify(credentials.Contrasena, usuario_dict["Contrasena"]):
        #     raise HTTPException(...)
        
        if usuario_dict["Contrasena"] != credentials.Contrasena:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos"
            )
        
        # Generar token simple (en producción usar JWT)
        token = secrets.token_urlsafe(32)
        
        # Actualizar último acceso
        from datetime import datetime
        cursor.execute(
            "UPDATE usuarios_sistema SET Ultimo_Acceso = ? WHERE Codigo = ?",
            (datetime.now().isoformat(), usuario_dict["Codigo"])
        )
        db.commit()
        
        # Remover contraseña del objeto usuario
        usuario_dict.pop("Contrasena", None)
        
        logger.info(f"Usuario {usuario_dict['Usuario']} inició sesión exitosamente")
        
        return {
            "usuario": usuario_dict,
            "token": token
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al autenticar usuario: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la autenticación: {str(e)}"
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    """
    Cerrar sesión del usuario
    
    Nota: En producción con JWT, esto invalidaría el token en el servidor
    """
    return {"message": "Sesión cerrada exitosamente"}


@router.get("/me")
async def get_current_user(db: Connection = Depends(get_db)):
    """
    Obtener información del usuario actual
    
    Nota: En producción, extraer el usuario del token JWT
    Por ahora, este endpoint está simplificado y requiere implementación completa con JWT
    """
    # TODO: Implementar extracción de usuario desde token JWT
    # Por ahora, retornar un error indicando que se necesita implementar
    # El frontend no usará este endpoint por ahora, solo verificará localStorage
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint pendiente de implementación con JWT"
    )
