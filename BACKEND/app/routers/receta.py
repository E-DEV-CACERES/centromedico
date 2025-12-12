"""
Router para gestión de recetas
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlite3 import Connection, IntegrityError, OperationalError
from typing import List, Optional
from app.database import get_db
from app.models import Receta, RecetaCreate, RecetaUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.get("/", response_model=List[Receta])
async def listar_recetas(
    db: Connection = Depends(get_db),
    codigo_paciente: Optional[int] = Query(None, description="Filtrar por paciente"),
    codigo_doctor: Optional[int] = Query(None, description="Filtrar por doctor")
):
    """
    Listar todas las recetas con filtros opcionales
    
    - **codigo_paciente**: Filtrar por paciente
    - **codigo_doctor**: Filtrar por doctor
    """
    try:
        cursor = db.cursor()
        
        query = "SELECT * FROM receta WHERE 1=1"
        params = []
        
        if codigo_paciente:
            query += " AND Codigo_Paciente = ?"
            params.append(codigo_paciente)
        
        if codigo_doctor:
            query += " AND Codigo_Doctor = ?"
            params.append(codigo_doctor)
        
        query += " ORDER BY Fecha_Receta DESC"
        
        cursor.execute(query, params)
        recetas = cursor.fetchall()
        return [dict(row) for row in recetas] if recetas else []
    
    except OperationalError as e:
        logger.error(f"Error de base de datos al listar recetas: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al acceder a la base de datos"
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar recetas: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )


@router.get("/completas", response_model=List[dict])
async def listar_recetas_completas(
    db: Connection = Depends(get_db),
    codigo_doctor: Optional[int] = Query(None, description="Filtrar por doctor")
):
    """
    Listar todas las recetas con información completa de las tablas relacionadas
    
    Incluye información de:
    - Receta (todos los campos)
    - Paciente (Nombre, Apellidos, etc.)
    - Doctor (Nombre, Apellidos, Especialidad, etc.)
    - Consulta (si está asociada)
    
    - **codigo_doctor**: Filtrar por doctor (opcional)
    """
    try:
        cursor = db.cursor()
        
        # Verificar que la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='receta'")
        if not cursor.fetchone():
            logger.error("La tabla 'receta' no existe en la base de datos")
            raise HTTPException(
                status_code=500,
                detail="La tabla de recetas no existe en la base de datos"
            )
        
        # Verificar qué columnas de exámenes existen en consultas
        cursor.execute("PRAGMA table_info(consultas)")
        columnas_consulta = [col[1] for col in cursor.fetchall()]
        
        # Construir SELECT dinámicamente según las columnas disponibles
        campos_examenes = []
        if "Examenes_Solicitados" in columnas_consulta:
            campos_examenes.append("c.Examenes_Solicitados AS Consulta_Examenes_Solicitados")
        if "Examenes_Descripcion" in columnas_consulta:
            campos_examenes.append("c.Examenes_Descripcion AS Consulta_Examenes_Descripcion")
        if "Examenes_Sugeridos" in columnas_consulta:
            campos_examenes.append("c.Examenes_Sugeridos AS Consulta_Examenes_Sugeridos")
        if "Examenes_Sugeridos_Descripcion" in columnas_consulta:
            campos_examenes.append("c.Examenes_Sugeridos_Descripcion AS Consulta_Examenes_Sugeridos_Descripcion")
        
        campos_examenes_str = ",\n                ".join(campos_examenes) if campos_examenes else ""
        if campos_examenes_str:
            campos_examenes_str = ",\n                " + campos_examenes_str
        
        # Query con JOINs para obtener información completa
        query = f"""
            SELECT 
                r.Codigo,
                r.Codigo_Paciente,
                r.Codigo_Doctor,
                r.Codigo_Consulta,
                r.Nombre_Paciente,
                r.Fecha_Receta,
                r.Medicamento,
                r.Instrucciones,
                r.Fecha_Creacion,
                r.Fecha_Modificacion,
                p.Nombre AS Paciente_Nombre,
                p.Apellidos AS Paciente_Apellidos,
                p.Numero_Celular AS Paciente_Telefono,
                p.Fecha_Nacimiento AS Paciente_Fecha_Nacimiento,
                d.Nombre AS Doctor_Nombre,
                d.Apellidos AS Doctor_Apellidos,
                d.Especialidad AS Doctor_Especialidad,
                d.Numero_Celular AS Doctor_Telefono,
                d.Correo AS Doctor_Email,
                d.Estado AS Doctor_Estado,
                c.Tipo_de_Consulta AS Consulta_Tipo,
                c.Fecha_de_Consulta AS Consulta_Fecha,
                c.Estado AS Consulta_Estado,
                c.Diagnostico AS Consulta_Diagnostico{campos_examenes_str}
            FROM receta r
            LEFT JOIN pacientes p ON r.Codigo_Paciente = p.Codigo
            LEFT JOIN doctor d ON r.Codigo_Doctor = d.Codigo
            LEFT JOIN consultas c ON r.Codigo_Consulta = c.Codigo
            WHERE 1=1
        """
        
        params = []
        
        if codigo_doctor:
            query += " AND r.Codigo_Doctor = ?"
            params.append(codigo_doctor)
        
        query += " ORDER BY r.Fecha_Receta DESC"
        
        logger.info(f"Ejecutando query: {query}")
        logger.info(f"Parámetros: {params}")
        
        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()
        except Exception as query_error:
            logger.error(f"Error al ejecutar query: {query_error}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error en la consulta SQL: {str(query_error)}"
            )
        
        logger.info(f"Recetas encontradas: {len(rows)}")
        
        # Si no hay recetas, retornar lista vacía
        if not rows:
            logger.info("No se encontraron recetas")
            return []
        
        # Convertir a diccionarios con estructura clara
        recetas_completas = []
        for idx, row in enumerate(rows):
            try:
                # Convertir row a diccionario primero
                if row is None:
                    logger.warning(f"Fila {idx} es None, omitiendo")
                    continue
                
                # Convertir Row a diccionario
                row_dict = dict(row)
                
                logger.debug(f"Procesando receta {row_dict.get('Codigo')}")
                
                receta_dict = {
                    # Datos de la receta
                    "receta": {
                        "Codigo": row_dict.get("Codigo"),
                        "Codigo_Paciente": row_dict.get("Codigo_Paciente"),
                        "Codigo_Doctor": row_dict.get("Codigo_Doctor"),
                        "Codigo_Consulta": row_dict.get("Codigo_Consulta"),
                        "Nombre_Paciente": row_dict.get("Nombre_Paciente"),
                        "Fecha_Receta": row_dict.get("Fecha_Receta"),
                        "Medicamento": row_dict.get("Medicamento"),
                        "Instrucciones": row_dict.get("Instrucciones"),
                        "Fecha_Creacion": row_dict.get("Fecha_Creacion"),
                        "Fecha_Modificacion": row_dict.get("Fecha_Modificacion")
                    },
                    # Información del paciente
                    "paciente": {
                        "Codigo": row_dict.get("Codigo_Paciente"),
                        "Nombre": row_dict.get("Paciente_Nombre"),
                        "Apellidos": row_dict.get("Paciente_Apellidos"),
                        "Telefono": row_dict.get("Paciente_Telefono"),
                        "Fecha_Nacimiento": row_dict.get("Paciente_Fecha_Nacimiento")
                    } if row_dict.get("Codigo_Paciente") else None,
                    # Información del doctor
                    "doctor": {
                        "Codigo": row_dict.get("Codigo_Doctor"),
                        "Nombre": row_dict.get("Doctor_Nombre"),
                        "Apellidos": row_dict.get("Doctor_Apellidos"),
                        "Especialidad": row_dict.get("Doctor_Especialidad"),
                        "Telefono": row_dict.get("Doctor_Telefono"),
                        "Email": row_dict.get("Doctor_Email"),
                        "Estado": row_dict.get("Doctor_Estado")
                    } if row_dict.get("Codigo_Doctor") else None,
                    # Información de la consulta
                    "consulta": {
                        "Codigo": row_dict.get("Codigo_Consulta"),
                        "Tipo_de_Consulta": row_dict.get("Consulta_Tipo"),
                        "Fecha_de_Consulta": row_dict.get("Consulta_Fecha"),
                        "Estado": row_dict.get("Consulta_Estado"),
                        "Diagnostico": row_dict.get("Consulta_Diagnostico"),
                        "Examenes_Solicitados": bool(row_dict.get("Consulta_Examenes_Solicitados")) if "Consulta_Examenes_Solicitados" in row_dict and row_dict.get("Consulta_Examenes_Solicitados") is not None else None,
                        "Examenes_Descripcion": row_dict.get("Consulta_Examenes_Descripcion") if "Consulta_Examenes_Descripcion" in row_dict else None,
                        "Examenes_Sugeridos": bool(row_dict.get("Consulta_Examenes_Sugeridos")) if "Consulta_Examenes_Sugeridos" in row_dict and row_dict.get("Consulta_Examenes_Sugeridos") is not None else None,
                        "Examenes_Sugeridos_Descripcion": row_dict.get("Consulta_Examenes_Sugeridos_Descripcion") if "Consulta_Examenes_Sugeridos_Descripcion" in row_dict else None
                    } if row_dict.get("Codigo_Consulta") else None
                }
                recetas_completas.append(receta_dict)
            except Exception as e:
                logger.error(f"Error al procesar fila de receta: {e}", exc_info=True)
                logger.error(f"Fila: {dict(row) if row else 'None'}")
                # Continuar con la siguiente fila en lugar de fallar completamente
                continue
        
        logger.info(f"Recetas procesadas exitosamente: {len(recetas_completas)}")
        return recetas_completas
    
    except OperationalError as e:
        logger.error(f"Error de base de datos al listar recetas completas: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al acceder a la base de datos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar recetas completas: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/{codigo}", response_model=Receta)
async def obtener_receta(codigo: int, db: Connection = Depends(get_db)):
    """Obtener una receta por código"""
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM receta WHERE Codigo = ?", (codigo,))
        receta = cursor.fetchone()
        
        if not receta:
            raise HTTPException(
                status_code=404,
                detail=f"Receta con código {codigo} no encontrada"
            )
        
        return dict(receta)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener receta {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener la receta"
        )


@router.post("/", response_model=Receta, status_code=201)
async def crear_receta(receta: RecetaCreate, db: Connection = Depends(get_db)):
    """
    Crear una nueva receta con validaciones
    
    - Valida que paciente, doctor y consulta existan
    - Usa transacciones para garantizar integridad
    """
    cursor = db.cursor()
    
    try:
        logger.info(f"Recibiendo solicitud para crear receta: {receta.model_dump()}")
        
        # Validar que se proporcionen los campos requeridos
        if not receta.Codigo_Paciente:
            raise HTTPException(
                status_code=400,
                detail="Codigo_Paciente es requerido"
            )
        
        if not receta.Codigo_Doctor:
            raise HTTPException(
                status_code=400,
                detail="Codigo_Doctor es requerido"
            )
        
        # Validar que Medicamento esté presente (requerido para recetas)
        if not receta.Medicamento or not receta.Medicamento.strip():
            raise HTTPException(
                status_code=400,
                detail="Medicamento es requerido"
            )
        
        # Verificar que paciente existe
        cursor.execute("SELECT Codigo FROM pacientes WHERE Codigo = ?", (receta.Codigo_Paciente,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con código {receta.Codigo_Paciente} no encontrado"
            )
        
        # Verificar que doctor existe
        cursor.execute("SELECT Codigo FROM doctor WHERE Codigo = ?", (receta.Codigo_Doctor,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Doctor con código {receta.Codigo_Doctor} no encontrado"
            )
        
        # Verificar que consulta existe si se proporciona
        if receta.Codigo_Consulta:
            cursor.execute("SELECT Codigo FROM consultas WHERE Codigo = ?", (receta.Codigo_Consulta,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Consulta con código {receta.Codigo_Consulta} no encontrada"
                )
        
        # Preparar datos - asegurar que Fecha_Receta siempre tenga un valor
        fecha_receta = datetime.now()
        if receta.Fecha_Receta:
            if isinstance(receta.Fecha_Receta, datetime):
                fecha_receta = receta.Fecha_Receta
            elif isinstance(receta.Fecha_Receta, str):
                try:
                    fecha_receta = datetime.fromisoformat(receta.Fecha_Receta.replace('Z', '+00:00'))
                except ValueError:
                    try:
                        fecha_receta = datetime.strptime(receta.Fecha_Receta, "%Y-%m-%dT%H:%M:%S")
                    except ValueError:
                        fecha_receta = datetime.now()
        
        datos = {
            "Codigo_Paciente": receta.Codigo_Paciente,
            "Codigo_Doctor": receta.Codigo_Doctor,
            "Codigo_Consulta": receta.Codigo_Consulta,
            "Nombre_Paciente": receta.Nombre_Paciente,
            "Fecha_Receta": fecha_receta.isoformat(),
            "Medicamento": receta.Medicamento,
            "Instrucciones": receta.Instrucciones
        }
        
        # Construir query de forma segura - filtrar None pero mantener campos opcionales
        # Nota: Codigo_Paciente, Codigo_Doctor y Fecha_Receta son requeridos
        campos = [k for k, v in datos.items() if v is not None]
        valores = [v for v in datos.values() if v is not None]
        
        # Validar que tenemos al menos los campos mínimos requeridos
        campos_requeridos = ["Codigo_Paciente", "Codigo_Doctor", "Fecha_Receta", "Medicamento"]
        campos_faltantes = [campo for campo in campos_requeridos if campo not in campos]
        if campos_faltantes:
            raise HTTPException(
                status_code=400,
                detail=f"Campos requeridos faltantes: {', '.join(campos_faltantes)}"
            )
        
        placeholders = ", ".join(["?" for _ in valores])
        campos_str = ", ".join(campos)
        
        logger.info(f"Insertando receta con campos: {campos_str}")
        logger.info(f"Valores: {valores}")
        
        try:
            cursor.execute(
                f"INSERT INTO receta ({campos_str}) VALUES ({placeholders})",
                valores
            )
        except Exception as insert_error:
            logger.error(f"Error al ejecutar INSERT: {insert_error}", exc_info=True)
            logger.error(f"Query: INSERT INTO receta ({campos_str}) VALUES ({placeholders})")
            logger.error(f"Valores: {valores}")
            raise
        
        codigo = cursor.lastrowid
        db.commit()
        
        cursor.execute("SELECT * FROM receta WHERE Codigo = ?", (codigo,))
        nueva_receta = cursor.fetchone()
        
        if not nueva_receta:
            raise HTTPException(
                status_code=500,
                detail="Error al recuperar la receta creada"
            )
        
        logger.info(f"Receta {codigo} creada exitosamente")
        return dict(nueva_receta)
    
    except HTTPException:
        db.rollback()
        raise
    except ValueError as e:
        db.rollback()
        logger.error(f"Error de validación de datos: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Error de validación: {str(e)}"
        )
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear receta: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Error de integridad de datos: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear receta: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear la receta: {str(e)}"
        )


@router.put("/{codigo}", response_model=Receta)
async def actualizar_receta(
    codigo: int,
    receta: RecetaUpdate,
    db: Connection = Depends(get_db)
):
    """Actualizar una receta existente"""
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT * FROM receta WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Receta con código {codigo} no encontrada"
            )
        
        # Preparar datos de actualización
        datos = receta.model_dump(exclude_unset=True)
        if not datos:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron datos para actualizar"
            )
        
        # Validar relaciones si se actualizan
        if "Codigo_Paciente" in datos:
            cursor.execute("SELECT Codigo FROM pacientes WHERE Codigo = ?", (datos["Codigo_Paciente"],))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Paciente con código {datos['Codigo_Paciente']} no encontrado"
                )
        
        if "Codigo_Doctor" in datos:
            cursor.execute("SELECT Codigo FROM doctor WHERE Codigo = ?", (datos["Codigo_Doctor"],))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Doctor con código {datos['Codigo_Doctor']} no encontrado"
                )
        
        if "Codigo_Consulta" in datos and datos["Codigo_Consulta"]:
            cursor.execute("SELECT Codigo FROM consultas WHERE Codigo = ?", (datos["Codigo_Consulta"],))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Consulta con código {datos['Codigo_Consulta']} no encontrada"
                )
        
        # Convertir fecha si existe
        if "Fecha_Receta" in datos and datos["Fecha_Receta"]:
            if hasattr(datos["Fecha_Receta"], 'isoformat'):
                datos["Fecha_Receta"] = datos["Fecha_Receta"].isoformat()
        
        # Agregar fecha de modificación
        datos["Fecha_Modificacion"] = datetime.now().isoformat()
        
        # Construir query de actualización
        campos = [f"{k} = ?" for k in datos.keys()]
        valores = list(datos.values())
        valores.append(codigo)
        
        cursor.execute(
            f"UPDATE receta SET {', '.join(campos)} WHERE Codigo = ?",
            valores
        )
        db.commit()
        
        cursor.execute("SELECT * FROM receta WHERE Codigo = ?", (codigo,))
        receta_actualizada = cursor.fetchone()
        
        logger.info(f"Receta {codigo} actualizada exitosamente")
        return dict(receta_actualizada)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar receta {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar receta {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar la receta"
        )


@router.delete("/{codigo}", status_code=204)
async def eliminar_receta(codigo: int, db: Connection = Depends(get_db)):
    """
    Eliminar una receta
    
    ⚠️ Advertencia: En producción, las recetas médicas generalmente no se eliminan.
    Considera usar soft delete o mantener un registro histórico.
    """
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT Codigo FROM receta WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Receta con código {codigo} no encontrada"
            )
        
        cursor.execute("DELETE FROM receta WHERE Codigo = ?", (codigo,))
        db.commit()
        
        logger.info(f"Receta {codigo} eliminada exitosamente")
        return None
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al eliminar receta {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar la receta debido a registros relacionados"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar receta {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar la receta"
        )
