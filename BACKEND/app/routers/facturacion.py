"""
Router para gestión de facturación
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlite3 import Connection, IntegrityError, OperationalError
from typing import List, Optional
from app.database import get_db
from app.models import Facturacion, FacturacionCreate, FacturacionUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.get("/", response_model=List[Facturacion])
async def listar_facturas(
    db: Connection = Depends(get_db),
    codigo_paciente: Optional[int] = Query(None, description="Filtrar por paciente"),
    estado_pago: Optional[str] = Query(None, description="Filtrar por estado de pago")
):
    """
    Listar todas las facturas con filtros opcionales
    
    - **codigo_paciente**: Filtrar por paciente
    - **estado_pago**: Filtrar por estado de pago (Pagado, Pendiente, Cancelado)
    """
    try:
        cursor = db.cursor()
        
        query = "SELECT * FROM facturacion WHERE 1=1"
        params = []
        
        if codigo_paciente:
            query += " AND Codigo_Paciente = ?"
            params.append(codigo_paciente)
        
        if estado_pago:
            query += " AND Estado_Pago = ?"
            params.append(estado_pago)
        
        query += " ORDER BY Fecha_Factura DESC"
        
        cursor.execute(query, params)
        facturas = cursor.fetchall()
        return [dict(row) for row in facturas] if facturas else []
    
    except OperationalError as e:
        logger.error(f"Error de base de datos al listar facturas: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al acceder a la base de datos"
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar facturas: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )


@router.get("/{codigo}", response_model=Facturacion)
async def obtener_factura(codigo: int, db: Connection = Depends(get_db)):
    """Obtener una factura por código"""
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM facturacion WHERE Codigo = ?", (codigo,))
        factura = cursor.fetchone()
        
        if not factura:
            raise HTTPException(
                status_code=404,
                detail=f"Factura con código {codigo} no encontrada"
            )
        
        return dict(factura)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener factura {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al obtener la factura"
        )


@router.post("/", response_model=Facturacion, status_code=201)
async def crear_factura(factura: FacturacionCreate, db: Connection = Depends(get_db)):
    """
    Crear una nueva factura con validaciones
    
    - Valida que paciente existe
    - Valida que consulta existe si se proporciona
    - Valida que el monto sea positivo
    - Usa transacciones para garantizar integridad
    """
    cursor = db.cursor()
    
    try:
        # Validar monto positivo
        if factura.Monto and factura.Monto <= 0:
            raise HTTPException(
                status_code=400,
                detail="El monto debe ser mayor a cero"
            )
        
        # Verificar que paciente existe
        cursor.execute("SELECT Codigo FROM pacientes WHERE Codigo = ?", (factura.Codigo_Paciente,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Paciente con código {factura.Codigo_Paciente} no encontrado"
            )
        
        # Verificar que consulta existe si se proporciona
        if factura.Codigo_Consulta:
            cursor.execute("SELECT Codigo FROM consultas_medicas WHERE Codigo = ?", (factura.Codigo_Consulta,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Consulta con código {factura.Codigo_Consulta} no encontrada"
                )
        
        # Preparar datos
        datos = {
            "Codigo_Paciente": factura.Codigo_Paciente,
            "Codigo_Consulta": factura.Codigo_Consulta,
            "Monto": factura.Monto,
            "Metodo_Pago": factura.Metodo_Pago,
            "Estado_Pago": factura.Estado_Pago or "Pendiente",
            "Numero_Factura": factura.Numero_Factura,
            "Fecha_Factura": factura.Fecha_Factura.isoformat() if factura.Fecha_Factura else datetime.now().isoformat()
        }
        
        # Construir query de forma segura
        campos = [k for k, v in datos.items() if v is not None]
        valores = [v for v in datos.values() if v is not None]
        placeholders = ", ".join(["?" for _ in valores])
        campos_str = ", ".join(campos)
        
        cursor.execute(
            f"INSERT INTO facturacion ({campos_str}) VALUES ({placeholders})",
            valores
        )
        
        codigo = cursor.lastrowid
        db.commit()
        
        cursor.execute("SELECT * FROM facturacion WHERE Codigo = ?", (codigo,))
        nueva_factura = cursor.fetchone()
        
        logger.info(f"Factura {codigo} creada exitosamente")
        return dict(nueva_factura)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear factura: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos. Verifica las relaciones."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear factura: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al crear la factura"
        )


@router.put("/{codigo}", response_model=Facturacion)
async def actualizar_factura(
    codigo: int,
    factura: FacturacionUpdate,
    db: Connection = Depends(get_db)
):
    """Actualizar una factura existente"""
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT * FROM facturacion WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Factura con código {codigo} no encontrada"
            )
        
        # Preparar datos de actualización
        datos = factura.model_dump(exclude_unset=True)
        if not datos:
            raise HTTPException(
                status_code=400,
                detail="No se proporcionaron datos para actualizar"
            )
        
        # Validar monto si se actualiza
        if "Monto" in datos and datos["Monto"] and datos["Monto"] <= 0:
            raise HTTPException(
                status_code=400,
                detail="El monto debe ser mayor a cero"
            )
        
        # Validar relaciones si se actualizan
        if "Codigo_Paciente" in datos:
            cursor.execute("SELECT Codigo FROM pacientes WHERE Codigo = ?", (datos["Codigo_Paciente"],))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Paciente con código {datos['Codigo_Paciente']} no encontrado"
                )
        
        if "Codigo_Consulta" in datos and datos["Codigo_Consulta"]:
            cursor.execute("SELECT Codigo FROM consultas_medicas WHERE Codigo = ?", (datos["Codigo_Consulta"],))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=404,
                    detail=f"Consulta con código {datos['Codigo_Consulta']} no encontrada"
                )
        
        # Convertir fecha si existe
        if "Fecha_Factura" in datos and datos["Fecha_Factura"]:
            if hasattr(datos["Fecha_Factura"], 'isoformat'):
                datos["Fecha_Factura"] = datos["Fecha_Factura"].isoformat()
        
        # Agregar fecha de modificación
        datos["Fecha_Modificacion"] = datetime.now().isoformat()
        
        # Construir query de actualización
        campos = [f"{k} = ?" for k in datos.keys()]
        valores = list(datos.values())
        valores.append(codigo)
        
        cursor.execute(
            f"UPDATE facturacion SET {', '.join(campos)} WHERE Codigo = ?",
            valores
        )
        db.commit()
        
        cursor.execute("SELECT * FROM facturacion WHERE Codigo = ?", (codigo,))
        factura_actualizada = cursor.fetchone()
        
        logger.info(f"Factura {codigo} actualizada exitosamente")
        return dict(factura_actualizada)
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar factura {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="Error de integridad de datos"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar factura {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al actualizar la factura"
        )


@router.delete("/{codigo}", status_code=204)
async def eliminar_factura(codigo: int, db: Connection = Depends(get_db)):
    """
    Eliminar una factura
    
    ⚠️ Advertencia: En producción, las facturas generalmente no se eliminan.
    Considera usar soft delete o cambiar el estado.
    """
    cursor = db.cursor()
    
    try:
        # Verificar que existe
        cursor.execute("SELECT Codigo FROM facturacion WHERE Codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=404,
                detail=f"Factura con código {codigo} no encontrada"
            )
        
        cursor.execute("DELETE FROM facturacion WHERE Codigo = ?", (codigo,))
        db.commit()
        
        logger.info(f"Factura {codigo} eliminada exitosamente")
        return None
    
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al eliminar factura {codigo}: {e}")
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar la factura debido a registros relacionados"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error al eliminar factura {codigo}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al eliminar la factura"
        )
