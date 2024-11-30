import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from clinica.models import tabla_citas
from clinica.services.gestion_de_citas import GestionCitas
from clinica.dbconfig import SessionLocal
from clinica_api.schemas import CitaCreate, CitaUpdate, CitaResponse
from typing import List, Optional
import logging

# Configuración del logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/citas",
    tags=["Citas"],
    responses={
        404: {"description": "Cita no encontrada"},
        500: {"description": "Error interno del servidor"},
        400: {"description": "Error de validación"}
    }
)

def get_db():
    """Proporciona una sesión de base de datos para las operaciones."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/exportar", 
            response_model=dict,
            summary="Exportar citas a JSON",
            description="Exporta todas las citas almacenadas en la base de datos a un archivo JSON")
async def exportar_citas_a_json(db: Session = Depends(get_db)):
    gestion_citas = GestionCitas(db)
    try:
        # Asegurarse de que el directorio existe
        os.makedirs(os.path.join(os.getcwd(), 'clinica/data'), exist_ok=True)
        
        ruta_exportada = os.path.join(os.getcwd(), 'clinica/data/tabla_citas.json')
        resultado = gestion_citas.exportar_citas_a_json(ruta_json=ruta_exportada)
        
        if os.path.exists(ruta_exportada):
            with open(ruta_exportada, 'r') as f:
                if not f.read().strip():
                    raise HTTPException(
                        status_code=500,
                        detail="El archivo de exportación está vacío"
                    )
                    
        return {
            "message": "Citas exportadas exitosamente",
            "path": ruta_exportada,
            "resultado": resultado
        }
    except Exception as e:
        logger.error(f"Error al exportar citas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al exportar citas: {str(e)}"
        )

@router.get("/obtener_ids", 
           response_model=dict,
           summary="Obtener IDs de ejemplo",
           description="Obtiene IDs de ejemplo de una cita para referencia")
async def obtener_ids(db: Session = Depends(get_db)):
    try:
        cita = db.query(tabla_citas).first()
        if not cita:
            logger.warning("No se encontraron citas en la base de datos")
            raise HTTPException(status_code=404, detail="No se encontró ninguna cita")
        
        return {
            "id_cliente": cita.id_cliente,
            "id_cita": cita.id_cita,
            "id_mascota": cita.id_mascota
        }
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al obtener IDs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", 
            response_model=CitaResponse,
            status_code=201,
            summary="Registrar nueva cita",
            description="Crea una nueva cita en el sistema")
async def registrar_cita(
    cita: CitaCreate, 
    db: Session = Depends(get_db)
):
    gestion_citas = GestionCitas(db)
    try:
        logger.info(f"Intentando registrar nueva cita: {cita.model_dump()}")
        nueva_cita = gestion_citas.registrar_cita(cita.model_dump())
        logger.info(f"Cita registrada exitosamente con ID: {nueva_cita.id_cita}")
        return CitaResponse.model_validate(nueva_cita)
    except ValueError as ve:
        logger.error(f"Error de validación al registrar cita: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except SQLAlchemyError as sae:
        logger.error(f"Error de base de datos al registrar cita: {str(sae)}")
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(sae)}")
    except Exception as e:
        logger.error(f"Error inesperado al registrar cita: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

@router.get("/", 
           response_model=List[CitaResponse],
           summary="Listar citas",
           description="Obtiene todas las citas con opción de filtrado por estado")
async def ver_todas_las_citas(
    estado: Optional[str] = Query(None, description="Estado de la cita (Pendiente, Finalizada, Cancelada)"),
    skip: int = Query(0, description="Número de registros a saltar"),
    limit: int = Query(100, description="Número máximo de registros a retornar"),
    db: Session = Depends(get_db)
):
    gestion_citas = GestionCitas(db)
    try:
        logger.info(f"Consultando citas con filtros - Estado: {estado}, Skip: {skip}, Limit: {limit}")
        citas = gestion_citas.ver_todas_las_citas(estado=estado)
        return [CitaResponse.model_validate(cita) for cita in citas["citas"]]
    except Exception as e:
        logger.error(f"Error al listar citas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al listar citas: {str(e)}")

@router.get("/buscar/{id_mascota}/{id_cliente}", 
           response_model=CitaResponse,
           summary="Buscar cita",
           description="Busca una cita específica por ID de mascota y cliente")
async def buscar_cita(
    id_mascota: int, 
    id_cliente: int, 
    db: Session = Depends(get_db)
):
    gestion_citas = GestionCitas(db)
    try:
        logger.info(f"Buscando cita - ID Mascota: {id_mascota}, ID Cliente: {id_cliente}")
        cita = gestion_citas.buscar_cita(id_mascota, id_cliente)
        if not cita:
            logger.warning(f"No se encontró cita para Mascota ID: {id_mascota}, Cliente ID: {id_cliente}")
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        return CitaResponse.model_validate(cita)
    except Exception as e:
        logger.error(f"Error al buscar cita: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al buscar cita: {str(e)}")

@router.put("/{id_cita}", 
           response_model=CitaResponse,
           summary="Modificar cita",
           description="Actualiza los datos de una cita existente")
async def modificar_cita(
    id_cita: int, 
    cita: CitaUpdate, 
    db: Session = Depends(get_db)
):
    gestion_citas = GestionCitas(db)
    try:
        logger.info(f"Modificando cita ID: {id_cita}")
        resultado = gestion_citas.modificar_cita(id_cita, cita.model_dump(exclude_unset=True))
        if not resultado:
            logger.warning(f"No se encontró la cita ID: {id_cita} para modificar")
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        logger.info(f"Cita ID: {id_cita} modificada exitosamente")
        return CitaResponse.model_validate(resultado)
    except Exception as e:
        logger.error(f"Error al modificar cita: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al modificar cita: {str(e)}")

@router.delete("/{id_cita}", 
              response_model=dict,
              summary="Cancelar cita",
              description="Cancela una cita existente")
async def cancelar_cita(id_cita: int, db: Session = Depends(get_db)):
    gestion_citas = GestionCitas(db)
    try:
        logger.info(f"Cancelando cita ID: {id_cita}")
        resultado = gestion_citas.cancelar_cita(id_cita)
        if not resultado:
            logger.warning(f"No se encontró la cita ID: {id_cita} para cancelar")
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        logger.info(f"Cita ID: {id_cita} cancelada exitosamente")
        return {"message": "Cita cancelada exitosamente"}
    except Exception as e:
        logger.error(f"Error al cancelar cita: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al cancelar cita: {str(e)}")
    
@router.put("/finalizar/{id_cita}", 
           response_model=dict,
           summary="Finalizar cita",
           description="Finaliza una cita y registra el método de pago")
async def finalizar_cita(
    id_cita: int,
    metodo_pago: str = Query(..., description="Método de pago utilizado (Efectivo, Tarjeta, Bizum, Transferencia)"),
    db: Session = Depends(get_db)
):
    gestion_citas = GestionCitas(db)
    try:
        logger.info(f"Finalizando cita ID: {id_cita} con método de pago: {metodo_pago}")
        resultado = gestion_citas.finalizar_cita(id_cita, metodo_pago)
        if not resultado:
            logger.warning(f"No se encontró la cita ID: {id_cita} para finalizar")
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        logger.info(f"Cita ID: {id_cita} finalizada exitosamente")
        
        # Modificar la respuesta para incluir un mensaje de éxito
        return {
            "message": "Cita finalizada con éxito",
            "cita": CitaResponse.model_validate(resultado)
        }
    except ValueError as ve:
        logger.error(f"Error de validación al finalizar cita: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error al finalizar cita: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al finalizar cita: {str(e)}")
