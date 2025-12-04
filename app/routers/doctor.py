"""
Router para gestión de doctores
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlite3 import Connection, IntegrityError, OperationalError
from typing import List, Optional
from app.database import get_db
from app.models import Doctor, DoctorCreate, DoctorUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.get("/", response_model=List[Doctor])
async def listar_doctores(
    db: Connection = Depends(get_db),
    especialidad: Optional[str] = Query(None, description="Filtrar por especialidad"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre")
):
    """
    Listar todos los doctores con filtros opcionales
    
    - **especialidad**: Filtrar por especialidad
    - **estado**: Filtrar por estado (Activo, Inactivo, Vacaciones)
    - **nombre**: Filtrar por nombre (búsqueda parcial)
    """
    try:
        cursor = db.cursor()
        
        query = "SELECT * FROM doctor WHERE 1=1"
        params = []
        
        if especialidad:
            query += " AND Especialidad = ?"
            params.append(especialidad)
        
        if estado:
            query += " AND Estado = ?"
            params.append(estado)
        
        if nombre:
            query += " AND (Nombre LIKE ? OR Apellidos LIKE ?)"
            params.extend([f"%{nombre}%", f"%{nombre}%"])
        
        query += " ORDER BY Codigo DESC"
        
        cursor.execute(query, params)
        doctores = cursor.fetchall()
        return [dict(row) for row in doctores] if doctores else []
    
    except OperationalError as e:
        logger.error(f"Error de base de datos al listar doctores: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al acceder a la base de datos"
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar doctores: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )


@router.get("/{codigo}", response_model=Doctor)
async def obtener_doctor(codigo: int, db: Connection = Depends(get_db)):
    """Obtener un doctor por código"""
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM doctor WHERE Codigo = ?", (codigo,))
        doctor = cursor.fetchone()
        
        if not doctor:
            raise HTTPException(
                status_code=404,
                detail=f"Doctor con código {codigo} no encontrado"
            )
        
        return dict(doctor)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener doctor {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener el doctor"
        )


@router.post("/", response_model=Doctor, status_code=201)
async def crear_doctor(doctor: DoctorCreate, db: Connection = Depends(get_db)):
    """
    Crear un nuevo doctor con validaciones
    
    - Valida que Numero_Colegiado sea único
    - Valida formato de correo (básico)
    - Usa transacciones para garantizar integridad
    """
    cursor = db.cursor()
    
    try:
        # Validar que Numero_Colegiado sea único si se proporciona
        if doctor.Numero_Colegiado:
            cursor.execute(
                "SELECT Codigo FROM doctor WHERE Numero_Colegiado = ?",
                (doctor.Numero_Colegiado,)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail=f"El número de colegiado {doctor.Numero_Colegiado} ya existe"
                )
        
        # Validación básica de correo
        if doctor.Correo and "@" not in doctor.Correo:
            raise HTTPException(
                status_code=400,
                detail="Formato de correo electrónico inválido"
            )
        
        # Preparar datos
        datos = {
            "Nombre": doctor.Nombre,
            "Apellidos": doctor.Apellidos,
            "Especialidad": doctor.Especialidad,
            "Direccion": doctor.Direccion,
            "Correo": doctor.Correo,
            "Genero": doctor.Genero,
            "Numero_Celular": doctor.Numero_Celular,
            "Numero_Colegiado": doctor.Numero_Colegiado,
            "Fecha_Contratacion": doctor.Fecha_Contratacion.isoformat() if doctor.Fecha_Contratacion else None,
            "Estado": doctor.Estado or "Activo",
            "Salario": doctor.Salario
        }
        
        # Construir query de forma segura
        campos = [k for k, v in datos.items() if v is not None]
        valores = [v for v in datos.values() if v is not None]
        placeholders = ", ".join(["?" for _ in valores])
        campos_str = ", ".join(campos)
        
        cursor.execute(
            f"INSERT INTO doctor ({campos_str}) VALUES ({placeholders})",
            valores
        )
        
        codigo = cursor.lastrowid
        db.commit()
        
        cursor.execute("SELECT * FROM doctor WHERE Codigo = ?", (codigo,))
        nuevo_doctor = cursor.fetchone()
        
        logger.info(f"Doctor {codigo} creado exitosamente")
        return dict(nuevo_doctor)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear doctor: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos. Verifica que el número de colegiado sea único."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear doctor: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al crear el doctor"
        )


@router.put("/{codigo}", response_model=Doctor)
async def actualizar_doctor(
    codigo: int,
    doctor: DoctorUpdate,
    db: Connection = Depends(get_db)
):
    """Actualizar un doctor existente"""
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT * FROM doctor WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Doctor con código {codigo} no encontrado"
            )
        
        # Preparar datos de actualización
        datos = doctor.model_dump(exclude_unset=True)
        if not datos:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron datos para actualizar"
            )
        
        # Validar Numero_Colegiado único si se actualiza
        if "Numero_Colegiado" in datos and datos["Numero_Colegiado"]:
            cursor.execute(
                "SELECT Codigo FROM doctor WHERE Numero_Colegiado = ? AND Codigo != ?",
                (datos["Numero_Colegiado"], codigo)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail=f"El número de colegiado {datos['Numero_Colegiado']} ya está en uso"
                )
        
        # Validar correo si se actualiza
        if "Correo" in datos and datos["Correo"] and "@" not in datos["Correo"]:
            raise HTTPException(
                status_code=400,
                detail="Formato de correo electrónico inválido"
            )
        
        # Convertir fecha si existe
        if "Fecha_Contratacion" in datos and datos["Fecha_Contratacion"]:
            if hasattr(datos["Fecha_Contratacion"], 'isoformat'):
                datos["Fecha_Contratacion"] = datos["Fecha_Contratacion"].isoformat()
        
        # Agregar fecha de modificación
        datos["Fecha_Modificacion"] = datetime.now().isoformat()
        
        # Construir query de actualización
        campos = [f"{k} = ?" for k in datos.keys()]
        valores = list(datos.values())
        valores.append(codigo)
        
        cursor.execute(
            f"UPDATE doctor SET {', '.join(campos)} WHERE Codigo = ?",
            valores
        )
        db.commit()
        
        cursor.execute("SELECT * FROM doctor WHERE Codigo = ?", (codigo,))
        doctor_actualizado = cursor.fetchone()
        
        logger.info(f"Doctor {codigo} actualizado exitosamente")
        return dict(doctor_actualizado)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar doctor {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar doctor {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar el doctor"
        )


@router.delete("/{codigo}", status_code=204)
async def eliminar_doctor(codigo: int, db: Connection = Depends(get_db)):
    """
    Eliminar un doctor
    
    ⚠️ Advertencia: Esto eliminará el doctor y puede afectar registros relacionados.
    En producción, considera usar soft delete o cambiar el estado a 'Inactivo'.
    """
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT Codigo FROM doctor WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Doctor con código {codigo} no encontrado"
            )
        
        # Verificar si tiene registros relacionados
        cursor.execute(
            "SELECT COUNT(*) FROM citas WHERE Codigo_Doctor = ?",
            (codigo,)
        )
        citas_count = cursor.fetchone()[0]
        
        if citas_count > 0:
            logger.warning(
                f"Eliminando doctor {codigo} con {citas_count} cita(s) relacionada(s)"
            )
        
        cursor.execute("DELETE FROM doctor WHERE Codigo = ?", (codigo,))
        db.commit()
        
        logger.info(f"Doctor {codigo} eliminado exitosamente")
        return None
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al eliminar doctor {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el doctor debido a registros relacionados"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar doctor {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar el doctor"
        )

