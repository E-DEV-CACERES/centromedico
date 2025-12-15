"""
Router para gestión de pacientes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlite3 import Connection, IntegrityError, OperationalError
from typing import List, Optional
from app.database import get_db
from app.models import Paciente, PacienteCreate, PacienteUpdate
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

router = APIRouter()


def normalize_date_string(date_str: str) -> Optional[str]:
    """
    Normaliza y valida una cadena de fecha a formato ISO 8601 con hora.
    
    Acepta formatos como:
    - YYYY-MM-DD (2024-01-01)
    - YYYY-M-D (2024-1-1)
    - YYYY-MM-D (2024-01-1)
    - YYYY-M-DD (2024-1-01)
    
    Retorna None si la fecha no es válida.
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    # Patrón regex para detectar fechas en formato YYYY-MM-DD (con variaciones)
    # Acepta: YYYY-MM-DD, YYYY-M-DD, YYYY-MM-D, YYYY-M-D
    date_pattern = r'^(\d{4})-(\d{1,2})-(\d{1,2})$'
    match = re.match(date_pattern, date_str.strip())
    
    if not match:
        return None
    
    try:
        year, month, day = match.groups()
        # Convertir a enteros y validar
        year = int(year)
        month = int(month)
        day = int(day)
        
        # Validar que la fecha sea realmente válida
        # Esto lanzará ValueError si la fecha no es válida (ej: 2024-13-45, 2024-02-30)
        datetime(year, month, day)
        
        # Formatear con ceros iniciales para formato estándar YYYY-MM-DD
        normalized_date = f"{year:04d}-{month:02d}-{day:02d}"
        # Agregar hora para formato ISO completo
        return f"{normalized_date}T00:00:00"
    except (ValueError, TypeError) as e:
        # Fecha inválida (ej: 2024-13-45, 2024-02-30)
        logger.warning(f"Fecha inválida detectada: {date_str} - {e}")
        return None


def row_to_dict(row) -> dict:
    """Convierte un Row de SQLite a un diccionario"""
    if row is None:
        return None
    result = {}
    for key in row.keys():
        value = row[key]
        # Convertir fechas de formato YYYY-MM-DD a datetime ISO si es necesario
        if key in ['Fecha_Nacimiento', 'Fecha_Creacion', 'Fecha_Modificacion'] and value:
            if isinstance(value, str):
                # Intentar normalizar la fecha usando validación robusta
                normalized = normalize_date_string(value)
                if normalized:
                    value = normalized
                # Si no se puede normalizar pero ya tiene formato ISO con hora, dejarlo como está
                elif 'T' in value or len(value) > 10:
                    # Ya tiene formato ISO completo o datetime, dejarlo como está
                    pass
        result[key] = value
    return result


@router.get("/", response_model=List[Paciente])
async def listar_pacientes(
    db: Connection = Depends(get_db),
    nombre: Optional[str] = Query(None, description="Filtrar por nombre"),
    apellidos: Optional[str] = Query(None, description="Filtrar por apellidos"),
    numero_identificacion: Optional[str] = Query(None, description="Filtrar por número de identificación")
):
    """
    Listar todos los pacientes con filtros opcionales
    
    - **nombre**: Filtrar por nombre (búsqueda parcial)
    - **apellidos**: Filtrar por apellidos (búsqueda parcial)
    """
    try:
        cursor = db.cursor()
        
        query = "SELECT * FROM pacientes WHERE 1=1"
        params = []
        
        if nombre:
            query += " AND Nombre LIKE ?"
            params.append(f"%{nombre}%")
        
        if apellidos:
            query += " AND Apellidos LIKE ?"
            params.append(f"%{apellidos}%")

        if numero_identificacion:
            query += " AND Numero_Identificacion LIKE ?"
            params.append(f"%{numero_identificacion}%")
        
        query += " ORDER BY Codigo DESC"
        
        cursor.execute(query, params)
        pacientes = cursor.fetchall()
        return [row_to_dict(row) for row in pacientes] if pacientes else []
    
    except OperationalError as e:
        logger.error(f"Error de base de datos al listar pacientes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al acceder a la base de datos"
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar pacientes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )


@router.get("/{codigo}", response_model=Paciente)
async def obtener_paciente(codigo: int, db: Connection = Depends(get_db)):
    """Obtener un paciente por código"""
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM pacientes WHERE Codigo = ?", (codigo,))
        paciente = cursor.fetchone()
        
        if not paciente:
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con código {codigo} no encontrado"
            )
        
        return row_to_dict(paciente)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener paciente {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener el paciente"
        )


@router.post("/", response_model=Paciente, status_code=201)
async def crear_paciente(paciente: PacienteCreate, db: Connection = Depends(get_db)):
    """
    Crear un nuevo paciente con validaciones
    
    - Valida datos requeridos
    - Verifica integridad referencial si hay Codigo_Seguro
    - Usa transacciones para garantizar integridad
    """
    cursor = db.cursor()
    
    try:
        # Validar Codigo_Seguro si se proporciona
        if paciente.Codigo_Seguro:
            cursor.execute("SELECT Codigo FROM seguros WHERE Codigo = ?", (paciente.Codigo_Seguro,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Seguro con código {paciente.Codigo_Seguro} no encontrado"
                )

        # Validar que Numero_Identificacion sea único si se proporciona
        if paciente.Numero_Identificacion:
            cursor.execute(
                "SELECT Codigo FROM pacientes WHERE Numero_Identificacion = ?",
                (paciente.Numero_Identificacion,)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail=f"El número de identificación {paciente.Numero_Identificacion} ya existe"
                )
        
        # Preparar datos
        datos = {
            "Nombre": paciente.Nombre,
            "Apellidos": paciente.Apellidos,
            "Edad": paciente.Edad,
            "Direccion": paciente.Direccion,
            "Numero_Celular": paciente.Numero_Celular,
            "Fecha_Nacimiento": paciente.Fecha_Nacimiento.isoformat() if paciente.Fecha_Nacimiento else None,
            "Tipo_Sangre": paciente.Tipo_Sangre,
            "Alergias": paciente.Alergias,
            "Contacto_Emergencia": paciente.Contacto_Emergencia,
            "Telefono_Emergencia": paciente.Telefono_Emergencia,
            "Codigo_Seguro": paciente.Codigo_Seguro,
            "Numero_Identificacion": paciente.Numero_Identificacion,
            "Tipo_Identificacion": paciente.Tipo_Identificacion,
        }
        
        # Construir query de forma segura
        campos = [k for k, v in datos.items() if v is not None]
        valores = [v for v in datos.values() if v is not None]
        placeholders = ", ".join(["?" for _ in valores])
        campos_str = ", ".join(campos)
        
        cursor.execute(
            f"INSERT INTO pacientes ({campos_str}) VALUES ({placeholders})",
            valores
        )
        
        codigo = cursor.lastrowid
        db.commit()
        
        cursor.execute("SELECT * FROM pacientes WHERE Codigo = ?", (codigo,))
        nuevo_paciente = cursor.fetchone()
        
        logger.info(f"Paciente {codigo} creado exitosamente")
        return row_to_dict(nuevo_paciente)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear paciente: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos. Verifica las relaciones."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear paciente: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al crear el paciente"
        )


@router.put("/{codigo}", response_model=Paciente)
async def actualizar_paciente(
    codigo: int,
    paciente: PacienteUpdate,
    db: Connection = Depends(get_db)
):
    """Actualizar un paciente existente"""
    cursor = db.cursor()
    
    try:
     
        cursor.execute("SELECT * FROM pacientes WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con código {codigo} no encontrado"
            )
        
    
        datos = paciente.model_dump(exclude_unset=True)
        if not datos:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron datos para actualizar"
            )
        
  
        if "Codigo_Seguro" in datos and datos["Codigo_Seguro"]:
            cursor.execute("SELECT Codigo FROM seguros WHERE Codigo = ?", (datos["Codigo_Seguro"],))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Seguro con código {datos['Codigo_Seguro']} no encontrado"
                )

        if "Numero_Identificacion" in datos and datos["Numero_Identificacion"]:
            cursor.execute(
                "SELECT Codigo FROM pacientes WHERE Numero_Identificacion = ? AND Codigo != ?",
                (datos["Numero_Identificacion"], codigo)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail=f"El número de identificación {datos['Numero_Identificacion']} ya está en uso"
                )
        
    
        if "Fecha_Nacimiento" in datos and datos["Fecha_Nacimiento"]:
            if hasattr(datos["Fecha_Nacimiento"], 'isoformat'):
                datos["Fecha_Nacimiento"] = datos["Fecha_Nacimiento"].isoformat()
        
        # Agregar fecha de modificación
        datos["Fecha_Modificacion"] = datetime.now().isoformat()
        
        # Construir query de actualización
        campos = [f"{k} = ?" for k in datos.keys()]
        valores = list(datos.values())
        valores.append(codigo)
        
        cursor.execute(
            f"UPDATE pacientes SET {', '.join(campos)} WHERE Codigo = ?",
            valores
        )
        db.commit()
        
        cursor.execute("SELECT * FROM pacientes WHERE Codigo = ?", (codigo,))
        paciente_actualizado = cursor.fetchone()
        
        logger.info(f"Paciente {codigo} actualizado exitosamente")
        return row_to_dict(paciente_actualizado)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar paciente {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar paciente {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar el paciente"
        )


@router.delete("/{codigo}", status_code=204)
async def eliminar_paciente(codigo: int, db: Connection = Depends(get_db)):
    """
    Eliminar un paciente
    
    ⚠️ Advertencia: Esto eliminará el paciente y puede afectar registros relacionados.
    En producción, considera usar soft delete.
    """
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT Codigo FROM pacientes WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con código {codigo} no encontrado"
            )
        
        # Verificar si tiene registros relacionados (opcional, para advertencia)
        cursor.execute(
            "SELECT COUNT(*) FROM consultas WHERE Codigo_Paciente = ?",
            (codigo,)
        )
        consultas_count = cursor.fetchone()[0]
        
        if consultas_count > 0:
            logger.warning(
                f"Eliminando paciente {codigo} con {consultas_count} consulta(s) relacionada(s)"
            )
        
        cursor.execute("DELETE FROM pacientes WHERE Codigo = ?", (codigo,))
        db.commit()
        
        logger.info(f"Paciente {codigo} eliminado exitosamente")
        return None
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al eliminar paciente {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar el paciente debido a registros relacionados"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar paciente {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar el paciente"
        )

