import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from clinica.services.gestion_mascotas import GestionMascotas
from clinica.dbconfig import SessionLocal
from clinica_api.schemas import MascotaCreate, MascotaUpdate, MascotaResponse
from typing import List, Optional
import logging

# Configuración del logger
logger = logging.getLogger(__name__)

router = APIRouter(
   prefix="/mascotas",
   tags=["Mascotas"],
   responses={
       404: {"description": "Mascota no encontrada"},
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
           summary="Exportar mascotas a JSON",
           description="Exporta todas las mascotas registradas a un archivo JSON")
async def exportar_mascotas(db: Session = Depends(get_db)):
   gestion_mascotas = GestionMascotas(db)
   try:
       ruta_exportada = os.path.abspath('clinica/data/tabla_mascotas.json')
       gestion_mascotas.exportar_mascotas_a_json(ruta_json=ruta_exportada)
       logger.info(f"Mascotas exportadas exitosamente a {ruta_exportada}")
       return {
           "message": "Mascotas exportadas exitosamente",
           "ruta": ruta_exportada
       }
   except SQLAlchemyError as e:
       logger.error(f"Error de base de datos al exportar mascotas: {str(e)}")
       raise HTTPException(status_code=500, detail="Error al exportar mascotas a JSON")
   except Exception as e:
       logger.error(f"Error inesperado al exportar mascotas: {str(e)}")
       raise HTTPException(status_code=500, detail=str(e))

@router.post("/", 
           response_model=MascotaResponse,
           status_code=201,
           summary="Registrar nueva mascota",
           description="Registra una nueva mascota en el sistema")
async def registrar_mascota(
   mascota: MascotaCreate, 
   db: Session = Depends(get_db)
):
   gestion_mascotas = GestionMascotas(db)
   try:
       logger.info(f"Intentando registrar nueva mascota para cliente ID: {mascota.id_cliente}")
       resultado = gestion_mascotas.registrar_mascota(
           mascota.id_cliente, 
           mascota.model_dump()
       )
       
       if isinstance(resultado, str) and "Error" in resultado:
           logger.error(f"Error al registrar mascota: {resultado}")
           raise HTTPException(status_code=400, detail=resultado)
       
       logger.info(f"Mascota registrada exitosamente con ID: {resultado.id_mascota}")
       return resultado
   except SQLAlchemyError as e:
       logger.error(f"Error de base de datos al registrar mascota: {str(e)}")
       raise HTTPException(
           status_code=500, 
           detail="Error al registrar la mascota en la base de datos"
       )
   except Exception as e:
       logger.error(f"Error inesperado al registrar mascota: {str(e)}")
       raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id_mascota}", 
          response_model=MascotaResponse,
          summary="Modificar mascota",
          description="Actualiza los datos de una mascota existente")
async def modificar_mascota(
   id_mascota: int, 
   mascota: MascotaUpdate, 
   db: Session = Depends(get_db)
):
   gestion_mascotas = GestionMascotas(db)
   try:
       logger.info(f"Modificando mascota ID: {id_mascota}")
       resultado = gestion_mascotas.modificar_mascota(
           id_mascota, 
           mascota.model_dump(exclude_unset=True)
       )
       
       if isinstance(resultado, str) and "Error" in resultado:
           logger.warning(f"Error al modificar mascota: {resultado}")
           raise HTTPException(status_code=404, detail=resultado)
           
       logger.info(f"Mascota ID: {id_mascota} modificada exitosamente")
       return resultado
   except SQLAlchemyError as e:
       logger.error(f"Error de base de datos al modificar mascota: {str(e)}")
       raise HTTPException(
           status_code=500, 
           detail="Error al modificar la mascota en la base de datos"
       )
   except Exception as e:
       logger.error(f"Error inesperado al modificar mascota: {str(e)}")
       raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id_mascota}",
             response_model=dict,
             summary="Eliminar mascota",
             description="Elimina una mascota del sistema")
async def eliminar_mascota(id_mascota: int, db: Session = Depends(get_db)):
   gestion_mascotas = GestionMascotas(db)
   try:
       logger.info(f"Eliminando mascota ID: {id_mascota}")
       resultado = gestion_mascotas.eliminar_mascota(id_mascota)
       
       if isinstance(resultado, str) and "Error" in resultado:
           logger.warning(f"Error al eliminar mascota: {resultado}")
           raise HTTPException(status_code=404, detail=resultado)
           
       logger.info(f"Mascota ID: {id_mascota} eliminada exitosamente")
       return {"message": resultado}
   except SQLAlchemyError as e:
       logger.error(f"Error de base de datos al eliminar mascota: {str(e)}")
       raise HTTPException(
           status_code=500, 
           detail="Error al eliminar la mascota de la base de datos"
       )
   except Exception as e:
       logger.error(f"Error inesperado al eliminar mascota: {str(e)}")
       raise HTTPException(status_code=500, detail=str(e))

@router.get("/", 
          response_model=List[MascotaResponse],
          summary="Listar mascotas",
          description="Obtiene la lista de todas las mascotas registradas")
async def listar_mascotas(
   skip: int = Query(0, description="Número de registros a saltar"),
   limit: int = Query(100, description="Número máximo de registros a retornar"),
   db: Session = Depends(get_db)
):
   gestion_mascotas = GestionMascotas(db)
   try:
       logger.info("Consultando lista de mascotas")
       return gestion_mascotas.listar_mascotas()
   except SQLAlchemyError as e:
       logger.error(f"Error de base de datos al listar mascotas: {str(e)}")
       raise HTTPException(
           status_code=500, 
           detail="Error al listar las mascotas de la base de datos"
       )
   except Exception as e:
       logger.error(f"Error inesperado al listar mascotas: {str(e)}")
       raise HTTPException(status_code=500, detail=str(e))

@router.get("/buscar_por_nombre/{nombre_mascota}",
          summary="Buscar mascota por nombre",
          description="Busca una mascota por su nombre")
async def buscar_mascota_por_nombre(
   nombre_mascota: str, 
   db: Session = Depends(get_db)
):
   gestion_mascotas = GestionMascotas(db)
   try:
       logger.info(f"Buscando mascota por nombre: {nombre_mascota}")
       resultado = gestion_mascotas.buscar_mascota_por_nombre(nombre_mascota)
       if resultado is None:
           logger.warning(f"No se encontró mascota con nombre: {nombre_mascota}")
           raise HTTPException(status_code=404, detail="Mascota no encontrada")
       return resultado
   except SQLAlchemyError as e:
       logger.error(f"Error de base de datos al buscar mascota: {str(e)}")
       raise HTTPException(
           status_code=500, 
           detail="Error al buscar la mascota en la base de datos"
       )
   except Exception as e:
       logger.error(f"Error inesperado al buscar mascota: {str(e)}")
       raise HTTPException(status_code=500, detail=str(e))
 
@router.get("/cliente/{id_cliente}", 
           response_model=List[MascotaResponse],
           summary="Listar mascotas por cliente",
           description="Obtiene la lista de mascotas pertenecientes a un cliente específico")
async def listar_mascotas_por_cliente(
    id_cliente: int,
    db: Session = Depends(get_db)
):
    gestion_mascotas = GestionMascotas(db)
    try:
        logger.info(f"Consultando mascotas del cliente ID: {id_cliente}")
        mascotas = gestion_mascotas.listar_mascotas_por_cliente(id_cliente)
        return [MascotaResponse.model_validate(mascota) for mascota in mascotas]
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al listar mascotas por cliente: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Error al listar las mascotas del cliente"
        )
    except Exception as e:
        logger.error(f"Error inesperado al listar mascotas por cliente: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/fallecido/{id_cliente}/{nombre_mascota}",
          response_model=dict,
          summary="Marcar mascota como fallecida",
          description="Actualiza el estado de una mascota a fallecido")
async def marcar_mascota_como_fallecido(
   id_cliente: int, 
   nombre_mascota: str, 
   db: Session = Depends(get_db)
):
   gestion_mascotas = GestionMascotas(db)
   try:
       logger.info(f"Marcando como fallecida la mascota: {nombre_mascota} del cliente ID: {id_cliente}")
       resultado = gestion_mascotas.marcar_mascota_como_fallecido(id_cliente, nombre_mascota)
       
       if isinstance(resultado, str) and "Error" in resultado:
           logger.warning(f"Error al marcar mascota como fallecida: {resultado}")
           raise HTTPException(status_code=404, detail=resultado)
           
       logger.info(f"Mascota {nombre_mascota} marcada como fallecida exitosamente")
       return {"message": resultado}
   except SQLAlchemyError as e:
       logger.error(f"Error de base de datos al actualizar estado de mascota: {str(e)}")
       raise HTTPException(
           status_code=500, 
           detail="Error al actualizar el estado de la mascota en la base de datos"
       )
   except Exception as e:
       logger.error(f"Error inesperado al marcar mascota como fallecida: {str(e)}")
       raise HTTPException(status_code=500, detail=str(e))
   
@router.get("/buscar", 
        response_model=List[MascotaResponse],
        summary="Buscar mascotas",
        description="Busca mascotas por nombre y/o raza")
async def buscar_mascotas(
    nombre: Optional[str] = Query(None, description="Nombre de la mascota"),
    raza: Optional[str] = Query(None, description="Raza de la mascota"),
    db: Session = Depends(get_db)
):
    """Busca mascotas por nombre y/o raza"""
    gestion_mascotas = GestionMascotas(db)
    try:
        mascotas = gestion_mascotas.buscar_mascotas(nombre=nombre, raza=raza)
        return [MascotaResponse.model_validate(mascota) for mascota in mascotas]
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al buscar mascotas: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al buscar mascotas")