"""
Router para gestión de usuarios del sistema
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlite3 import Connection, IntegrityError, OperationalError
from typing import List, Optional, Dict, Any
from app.database import get_db, DATABASE_URL
from app.models import UsuarioSistema, UsuarioSistemaCreate, UsuarioSistemaUpdate
from datetime import datetime
import logging
import shutil
import os

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

router = APIRouter()


def row_to_dict(row) -> Dict[str, Any]:
    """Convierte un Row de SQLite a un diccionario, manejando None y tipos correctamente"""
    if row is None:
        return None
    result = {}
    for key in row.keys():
        value = row[key]
        # Convertir None a None explícitamente, mantener otros valores
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


@router.get("/", response_model=List[UsuarioSistema])
async def listar_usuarios(
    db: Connection = Depends(get_db),
    rol: Optional[str] = Query(None, description="Filtrar por rol"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo")
):
    """
    Listar todos los usuarios del sistema con filtros opcionales
    
    - **rol**: Filtrar por rol (Admin, Doctor, Recepcionista, etc.)
    - **activo**: Filtrar por estado activo (true/false)
    """
    try:
        cursor = db.cursor()
        
        # Verificar y crear tabla si no existe
        verificar_tabla_usuarios(cursor)
        db.commit()
        
        query = "SELECT * FROM usuarios_sistema WHERE 1=1"
        params = []
        
        if rol:
            query += " AND Rol = ?"
            params.append(rol)
        
        if activo is not None:
            query += " AND Activo = ?"
            params.append(1 if activo else 0)
        
        query += " ORDER BY Codigo DESC"
        
        cursor.execute(query, params)
        usuarios = cursor.fetchall()
        return [row_to_dict(row) for row in usuarios] if usuarios else []
    
    except OperationalError as e:
        logger.error(f"Error de base de datos al listar usuarios: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al acceder a la base de datos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar usuarios: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/{codigo}", response_model=UsuarioSistema)
async def obtener_usuario(codigo: int, db: Connection = Depends(get_db)):
    """Obtener un usuario por código"""
    try:
        cursor = db.cursor()
        
        # Verificar y crear tabla si no existe
        verificar_tabla_usuarios(cursor)
        db.commit()
        
        cursor.execute("SELECT * FROM usuarios_sistema WHERE Codigo = ?", (codigo,))
        usuario = cursor.fetchone()
        
        if not usuario:
            raise HTTPException(
                status_code=404,
                detail=f"Usuario con código {codigo} no encontrado"
            )
        
        return row_to_dict(usuario)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener usuario {codigo}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener el usuario: {str(e)}"
        )


@router.post("/", response_model=UsuarioSistema, status_code=201)
async def crear_usuario(usuario: UsuarioSistemaCreate, db: Connection = Depends(get_db)):
    """
    Crear un nuevo usuario del sistema con validaciones
    
    - Valida que el nombre de usuario sea único
    - Valida que doctor existe si se proporciona
    - Valida formato de contraseña (mínimo 6 caracteres)
    - ⚠️ NOTA: En producción, la contraseña debe estar hasheada con bcrypt
    """
    cursor = db.cursor()
    
    try:
        # Verificar y crear tabla si no existe
        verificar_tabla_usuarios(cursor)
        db.commit()
        
        # Validar que el nombre de usuario no existe
        cursor.execute("SELECT Codigo FROM usuarios_sistema WHERE Usuario = ?", (usuario.Usuario,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail=f"El nombre de usuario '{usuario.Usuario}' ya existe"
            )
        
        # Validar longitud mínima de contraseña
        if usuario.Contrasena and len(usuario.Contrasena) < 6:
            raise HTTPException(
                status_code=400,
                detail="La contraseña debe tener al menos 6 caracteres"
            )
        
        # Verificar que doctor existe si se proporciona
        if usuario.Codigo_Doctor:
            cursor.execute("SELECT Codigo FROM doctor WHERE Codigo = ?", (usuario.Codigo_Doctor,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Doctor con código {usuario.Codigo_Doctor} no encontrado"
                )
        
        # Preparar datos
        # ⚠️ IMPORTANTE: En producción, hashear la contraseña con bcrypt
        # from passlib.context import CryptContext
        # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # contrasena_hash = pwd_context.hash(usuario.Contrasena)
        
        fecha_actual = datetime.now().isoformat()
        datos = {
            "Usuario": usuario.Usuario,
            "Contrasena": usuario.Contrasena,  # TODO: Hashear con bcrypt en producción
            "Codigo_Doctor": usuario.Codigo_Doctor,
            "Rol": usuario.Rol or "Recepcionista",
            "Activo": 1 if (usuario.Activo is None or usuario.Activo == 1) else 0,
            "Fecha_Creacion": fecha_actual,
            "Fecha_Modificacion": fecha_actual
        }
        
        # Construir query de forma segura
        campos = [k for k, v in datos.items() if v is not None]
        valores = [v for v in datos.values() if v is not None]
        placeholders = ", ".join(["?" for _ in valores])
        campos_str = ", ".join(campos)
        
        cursor.execute(
            f"INSERT INTO usuarios_sistema ({campos_str}) VALUES ({placeholders})",
            valores
        )
        
        codigo = cursor.lastrowid
        db.commit()
        
        cursor.execute("SELECT * FROM usuarios_sistema WHERE Codigo = ?", (codigo,))
        nuevo_usuario = cursor.fetchone()
        
        if not nuevo_usuario:
            raise HTTPException(
                status_code=500,
                detail="Error al recuperar el usuario creado"
            )
        
        logger.info(f"Usuario {codigo} ({usuario.Usuario}) creado exitosamente")
        return row_to_dict(nuevo_usuario)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear usuario: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos. Verifica que el nombre de usuario sea único."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear usuario: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear el usuario: {str(e)}"
        )


@router.put("/{codigo}", response_model=UsuarioSistema)
async def actualizar_usuario(
    codigo: int,
    usuario: UsuarioSistemaUpdate,
    db: Connection = Depends(get_db)
):
    """
    Actualizar un usuario del sistema
    
    ⚠️ NOTA: Si se actualiza la contraseña, debe hashearse con bcrypt en producción
    """
    cursor = db.cursor()
    
    try:
        # Verificar y crear tabla si no existe
        verificar_tabla_usuarios(cursor)
        db.commit()
        
        # Verificar que existe
        cursor.execute("SELECT * FROM usuarios_sistema WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Usuario con código {codigo} no encontrado"
            )
        
        # Preparar datos de actualización
        datos = usuario.model_dump(exclude_unset=True)
        if not datos:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron datos para actualizar"
            )
        
        # Validar nombre de usuario único si se actualiza
        if "Usuario" in datos:
            cursor.execute(
                "SELECT Codigo FROM usuarios_sistema WHERE Usuario = ? AND Codigo != ?",
                (datos["Usuario"], codigo)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail=f"El nombre de usuario '{datos['Usuario']}' ya está en uso"
                )
        
        # Validar longitud de contraseña si se actualiza
        if "Contrasena" in datos and datos["Contrasena"]:
            if len(datos["Contrasena"]) < 6:
                raise HTTPException(
                    status_code=400,
                    detail="La contraseña debe tener al menos 6 caracteres"
                )
            # TODO: Hashear con bcrypt en producción
            # datos["Contrasena"] = pwd_context.hash(datos["Contrasena"])
        
        # Validar doctor si se actualiza
        if "Codigo_Doctor" in datos and datos["Codigo_Doctor"]:
            cursor.execute("SELECT Codigo FROM doctor WHERE Codigo = ?", (datos["Codigo_Doctor"],))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Doctor con código {datos['Codigo_Doctor']} no encontrado"
                )
        
        # Agregar fecha de modificación
        datos["Fecha_Modificacion"] = datetime.now().isoformat()
        
        # Construir query de actualización
        campos = [f"{k} = ?" for k in datos.keys()]
        valores = list(datos.values())
        valores.append(codigo)
        
        cursor.execute(
            f"UPDATE usuarios_sistema SET {', '.join(campos)} WHERE Codigo = ?",
            valores
        )
        db.commit()
        
        cursor.execute("SELECT * FROM usuarios_sistema WHERE Codigo = ?", (codigo,))
        usuario_actualizado = cursor.fetchone()
        
        if not usuario_actualizado:
            raise HTTPException(
                status_code=500,
                detail="Error al recuperar el usuario actualizado"
            )
        
        logger.info(f"Usuario {codigo} actualizado exitosamente")
        return row_to_dict(usuario_actualizado)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar usuario {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar usuario {codigo}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar el usuario: {str(e)}"
        )


@router.delete("/{codigo}", status_code=204)
async def eliminar_usuario(codigo: int, db: Connection = Depends(get_db)):
    """
    Eliminar un usuario del sistema
    
    ⚠️ Advertencia: En producción, considera usar soft delete (cambiar Activo a False)
    en lugar de eliminar físicamente el usuario.
    """
    cursor = db.cursor()
    
    try:
        # Verificar y crear tabla si no existe
        verificar_tabla_usuarios(cursor)
        db.commit()
        
        # Verificar que existe
        cursor.execute("SELECT Codigo FROM usuarios_sistema WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Usuario con código {codigo} no encontrado"
            )
        
        cursor.execute("DELETE FROM usuarios_sistema WHERE Codigo = ?", (codigo,))
        db.commit()
        
        logger.info(f"Usuario {codigo} eliminado exitosamente")
        return None
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al eliminar usuario {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el usuario debido a registros relacionados"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar usuario {codigo}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar el usuario: {str(e)}"
        )


@router.post("/backup")
async def crear_backup():
    """
    Crear una copia de seguridad de la base de datos
    
    Genera un archivo de backup con timestamp en el nombre.
    """
    try:
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.db"
        
        # Obtener la ruta del directorio actual (donde está el archivo de la base de datos)
        current_dir = os.path.dirname(os.path.abspath(DATABASE_URL))
        if not current_dir:
            current_dir = os.getcwd()
        
        backup_path = os.path.join(current_dir, backup_filename)
        
        # Obtener la ruta completa de la base de datos
        db_path = os.path.abspath(DATABASE_URL)
        
        # Verificar que el archivo de base de datos existe
        if not os.path.exists(db_path):
            raise HTTPException(
                status_code=404,
                detail="La base de datos no existe"
            )
        
        # Crear copia de seguridad usando SQLite backup API para mayor seguridad
        import sqlite3
        source_conn = sqlite3.connect(db_path)
        backup_conn = sqlite3.connect(backup_path)
        
        # Usar backup API de SQLite
        source_conn.backup(backup_conn)
        
        backup_conn.close()
        source_conn.close()
        
        logger.info(f"Backup creado exitosamente: {backup_filename}")
        
        return {
            "message": "Copia de seguridad creada exitosamente",
            "filename": backup_filename,
            "path": backup_path,
            "timestamp": timestamp
        }
    
    except FileNotFoundError as e:
        logger.error(f"Error al crear backup: archivo no encontrado - {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Error al crear backup: {str(e)}"
        )
    except PermissionError as e:
        logger.error(f"Error de permisos al crear backup: {e}")
        raise HTTPException(
            status_code=403,
            detail="No se tienen permisos para crear el backup"
        )
    except Exception as e:
        logger.error(f"Error inesperado al crear backup: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear la copia de seguridad: {str(e)}"
        )


@router.get("/backup/download/{filename}")
async def descargar_backup(filename: str):
    """
    Descargar un archivo de backup específico
    
    - **filename**: Nombre del archivo de backup a descargar
    """
    try:
        # Validar que el nombre del archivo sea seguro
        # Debe tener el prefijo 'backup_' para prevenir acceso a archivos no autorizados
        if (not filename.startswith('backup_') or 
            not filename.endswith('.db') or 
            '..' in filename or 
            '/' in filename or 
            '\\' in filename):
            raise HTTPException(
                status_code=400,
                detail="Nombre de archivo inválido. Solo se permiten archivos de backup con prefijo 'backup_'"
            )
        
        current_dir = os.path.dirname(os.path.abspath(DATABASE_URL))
        if not current_dir:
            current_dir = os.getcwd()
        
        backup_path = os.path.join(current_dir, filename)
        backup_path = os.path.abspath(backup_path)
        
        # Verificar que el archivo existe
        if not os.path.exists(backup_path):
            raise HTTPException(
                status_code=404,
                detail="El archivo de backup no existe"
            )
        
        return FileResponse(
            path=backup_path,
            filename=filename,
            media_type='application/octet-stream'
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al descargar backup {filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al descargar el backup: {str(e)}"
        )


@router.get("/backup/list")
async def listar_backups():
    """
    Listar todos los archivos de backup disponibles
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(DATABASE_URL))
        if not current_dir:
            current_dir = os.getcwd()
        
        backups = []
        if os.path.exists(current_dir):
            for filename in os.listdir(current_dir):
                if filename.startswith("backup_") and filename.endswith(".db"):
                    filepath = os.path.join(current_dir, filename)
                    file_stat = os.stat(filepath)
                    backups.append({
                        "filename": filename,
                        "size": file_stat.st_size,
                        "created": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                    })
        
        # Ordenar por fecha de creación (más recientes primero)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        return {
            "backups": backups,
            "count": len(backups)
        }
    
    except Exception as e:
        logger.error(f"Error al listar backups: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar los backups: {str(e)}"
        )
