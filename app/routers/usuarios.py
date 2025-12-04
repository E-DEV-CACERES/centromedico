"""
Router para gestión de usuarios del sistema
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlite3 import Connection, IntegrityError, OperationalError
from typing import List, Optional
from app.database import get_db
from app.models import UsuarioSistema, UsuarioSistemaCreate, UsuarioSistemaUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

router = APIRouter()


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
        return [dict(row) for row in usuarios] if usuarios else []
    
    except OperationalError as e:
        logger.error(f"Error de base de datos al listar usuarios: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al acceder a la base de datos"
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar usuarios: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )


@router.get("/{codigo}", response_model=UsuarioSistema)
async def obtener_usuario(codigo: int, db: Connection = Depends(get_db)):
    """Obtener un usuario por código"""
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM usuarios_sistema WHERE Codigo = ?", (codigo,))
        usuario = cursor.fetchone()
        
        if not usuario:
            raise HTTPException(
                status_code=404,
                detail=f"Usuario con código {codigo} no encontrado"
            )
        
        return dict(usuario)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener usuario {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener el usuario"
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
        
        datos = {
            "Usuario": usuario.Usuario,
            "Contrasena": usuario.Contrasena,  # TODO: Hashear con bcrypt en producción
            "Codigo_Doctor": usuario.Codigo_Doctor,
            "Rol": usuario.Rol or "Usuario",
            "Activo": usuario.Activo if usuario.Activo is not None else True
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
        
        logger.info(f"Usuario {codigo} ({usuario.Usuario}) creado exitosamente")
        return dict(nuevo_usuario)
    
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
        logger.error(f"Error inesperado al crear usuario: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al crear el usuario"
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
        
        logger.info(f"Usuario {codigo} actualizado exitosamente")
        return dict(usuario_actualizado)
    
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
        logger.error(f"Error inesperado al actualizar usuario {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar el usuario"
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
        logger.error(f"Error al eliminar usuario {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar el usuario"
        )
