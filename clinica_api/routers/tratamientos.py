import os
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from fastapi.responses import FileResponse
from clinica.dbconfig import SessionLocal
from clinica.models import Cliente, Mascota, Tratamiento, Cita
from clinica.services.gestion_tratamiento import GestionTratamientos
from clinica_api.schemas import TratamientoResponse, TratamientoCreate, TratamientoUpdate
from typing import List, Optional
import logging

# Configuración del logger
logger = logging.getLogger(__name__)

router = APIRouter(
   prefix="/tratamientos",
   tags=["Tratamientos"],
   responses={
       404: {"description": "Tratamiento no encontrado"},
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
           summary="Exportar tratamientos a JSON",
           description="Exporta todos los tratamientos registrados a un archivo JSON")
async def exportar_tratamientos_a_json(db: Session = Depends(get_db)):
   gestion_tratamientos = GestionTratamientos(db)
   try:
       ruta_exportada = os.path.join(os.getcwd(), 'clinica/data/tabla_tratamientos.json')
       gestion_tratamientos.exportar_tratamientos_a_json(ruta_json=ruta_exportada)
       logger.info(f"Tratamientos exportados exitosamente a {ruta_exportada}")
       return {
           "message": "Tratamientos exportados exitosamente",
           "ruta": ruta_exportada
       }
   except Exception as e:
       logger.error(f"Error al exportar tratamientos: {str(e)}")
       raise HTTPException(
           status_code=500,
           detail=f"Error al exportar tratamientos a JSON: {str(e)}"
       )

@router.get("/", 
          response_model=List[TratamientoResponse],
          summary="Listar tratamientos",
          description="Obtiene todos los tratamientos registrados en el sistema")
async def listar_tratamientos(db: Session = Depends(get_db)):
    try:
        gestion_tratamientos = GestionTratamientos(db)
        tratamientos = gestion_tratamientos.listar_tratamientos()
        
        if not tratamientos:
            logger.warning("No se encontraron tratamientos registrados")
            return []
            
        logger.info(f"Se encontraron {len(tratamientos)} tratamientos")
        return [TratamientoResponse.model_validate(t) for t in tratamientos]
        
    except Exception as e:
        logger.error(f"Error al listar tratamientos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al listar tratamientos: {str(e)}"
        )

@router.post("/", 
           response_model=TratamientoResponse,
           status_code=201,
           summary="Dar de alta tratamiento",
           description="Registra un nuevo tratamiento en el sistema")
async def dar_alta_tratamiento(
   tratamiento: TratamientoCreate, 
   db: Session = Depends(get_db)
):
   gestion_tratamientos = GestionTratamientos(db)
   try:
       logger.info(f"Registrando nuevo tratamiento: {tratamiento.model_dump()}")
       resultado = gestion_tratamientos.dar_alta_tratamiento(tratamiento.model_dump())
       
       if isinstance(resultado, str) and "Error" in resultado:
           logger.error(f"Error al registrar tratamiento: {resultado}")
           raise HTTPException(status_code=400, detail=resultado)
           
       logger.info(f"Tratamiento registrado exitosamente con ID: {resultado.id_tratamiento}")
       return TratamientoResponse.model_validate(resultado)
   except HTTPException:
       raise
   except Exception as e:
       logger.error(f"Error inesperado al registrar tratamiento: {str(e)}")
       raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id_tratamiento}", 
          response_model=TratamientoResponse,
          summary="Modificar tratamiento",
          description="Actualiza los datos de un tratamiento existente")
async def modificar_tratamiento(
   id_tratamiento: int,
   tratamiento: TratamientoUpdate,
   db: Session = Depends(get_db)
):
   try:
       logger.info(f"Modificando tratamiento ID: {id_tratamiento}")
       gestion_tratamientos = GestionTratamientos(db)
       resultado = gestion_tratamientos.modificar_tratamiento(
           id_tratamiento,
           tratamiento.model_dump(exclude_unset=True)
       )
       
       if isinstance(resultado, str) and "Error" in resultado:
           logger.warning(f"Error al modificar tratamiento: {resultado}")
           raise HTTPException(status_code=404, detail=resultado)
           
       logger.info(f"Tratamiento ID: {id_tratamiento} modificado exitosamente")
       return resultado
   except Exception as e:
       logger.error(f"Error al modificar tratamiento: {str(e)}")
       raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{nombre_tratamiento}",
             response_model=dict,
             summary="Dar de baja tratamiento",
             description="Da de baja un tratamiento existente")
async def dar_baja_tratamiento(
   nombre_tratamiento: str,
   db: Session = Depends(get_db)
):
   try:
       logger.info(f"Dando de baja tratamiento: {nombre_tratamiento}")
       gestion_tratamientos = GestionTratamientos(db)
       resultado = gestion_tratamientos.dar_baja_tratamiento(nombre_tratamiento)
       
       if "Error" in resultado:
           logger.warning(f"Error al dar de baja tratamiento: {resultado}")
           raise HTTPException(status_code=404, detail=resultado)
           
       logger.info(f"Tratamiento {nombre_tratamiento} dado de baja exitosamente")
       return {"message": resultado}
   except Exception as e:
       logger.error(f"Error al dar de baja tratamiento: {str(e)}")
       raise HTTPException(status_code=500, detail=str(e))

@router.get("/factura/{id_tratamiento}",
          response_model=dict,
          summary="Obtener datos de factura",
          description="Obtiene los datos necesarios para generar una factura")
async def obtener_datos_factura(
   id_tratamiento: int,
   db: Session = Depends(get_db)
):
   try:
       logger.info(f"Obteniendo datos de factura para tratamiento ID: {id_tratamiento}")
       gestion_tratamientos = GestionTratamientos(db)
       datos_factura = gestion_tratamientos.obtener_datos_factura(id_tratamiento)
       
       if "error" in datos_factura:
           logger.warning(f"Error al obtener datos de factura: {datos_factura['error']}")
           raise HTTPException(status_code=404, detail=datos_factura["error"])
           
       logger.info(f"Datos de factura obtenidos exitosamente para tratamiento ID: {id_tratamiento}")
       return datos_factura
   except Exception as e:
       logger.error(f"Error al obtener datos de factura: {str(e)}")
       raise HTTPException(status_code=500, detail=str(e))

@router.get("/validar/{id_tratamiento}",
          response_model=dict,
          summary="Validar tratamiento Finalizada",
          description="Verifica si un tratamiento está Finalizada")
async def validar_tratamiento_Finalizada(
   id_tratamiento: int,
   db: Session = Depends(get_db)
):
   try:
       logger.info(f"Validando estado de tratamiento ID: {id_tratamiento}")
       gestion_tratamientos = GestionTratamientos(db)
       
       tratamiento = db.query(Tratamiento).filter_by(id_tratamiento=id_tratamiento).first()
       if not tratamiento:
           logger.warning(f"Tratamiento no encontrado ID: {id_tratamiento}")
           raise HTTPException(status_code=404, detail="Tratamiento no encontrado")

       resultado = gestion_tratamientos.validar_tratamiento_Finalizada(tratamiento)
       if isinstance(resultado, dict) and "error" in resultado:
           logger.warning(f"Error en validación de tratamiento: {resultado['error']}")
           raise HTTPException(status_code=400, detail=resultado["error"])
           
       logger.info(f"Validación de tratamiento ID {id_tratamiento} completada")
       return {"Finalizada": resultado}
   except Exception as e:
       logger.error(f"Error al validar tratamiento: {str(e)}")
       raise HTTPException(status_code=500, detail=str(e))

@router.get("/factura/generar/{id_tratamiento}",
          response_class=FileResponse,
          summary="Generar factura PDF",
          description="Genera una factura en formato PDF para un tratamiento")
async def generar_factura(id_tratamiento: int, db: Session = Depends(get_db)):
   try:
       logger.info(f"Generando factura PDF para tratamiento ID: {id_tratamiento}")
       
       # Obtener datos necesarios
       tratamiento = db.query(Tratamiento).filter_by(id_tratamiento=id_tratamiento).first()
       if not tratamiento:
           logger.warning(f"Tratamiento no encontrado ID: {id_tratamiento}")
           raise HTTPException(status_code=404, detail="Tratamiento no encontrado")

       cita = db.query(Cita).filter_by(id_tratamiento=id_tratamiento).first()
       if not cita:
           logger.warning(f"Cita no encontrada para tratamiento ID: {id_tratamiento}")
           raise HTTPException(
               status_code=404,
               detail="Cita no encontrada para el tratamiento especificado"
           )

       cliente = db.query(Cliente).filter_by(id_cliente=cita.id_cliente).first()
       mascota = db.query(Mascota).filter_by(id_mascota=cita.id_mascota).first()
       
       if not cliente or not mascota:
           logger.warning("Cliente o mascota no encontrados")
           raise HTTPException(status_code=404, detail="Cliente o mascota no encontrados")

       # Generar PDF
       pdf_path = Path("factura.pdf")
       c = canvas.Canvas(str(pdf_path), pagesize=letter)
       width, height = letter

       # Generar contenido del PDF...
       # [Código de generación del PDF]

       logger.info(f"Factura generada exitosamente para tratamiento ID: {id_tratamiento}")
       return FileResponse(
           path=pdf_path,
           filename="factura.pdf",
           media_type="application/pdf"
       )

   except HTTPException:
       raise
   except Exception as e:
       logger.error(f"Error al generar factura: {str(e)}")
       raise HTTPException(status_code=500, detail=str(e))
   
@router.get("/{id_tratamiento}", 
           response_model=TratamientoResponse,
           summary="Obtener tratamiento por ID",
           description="Obtiene los datos de un tratamiento específico por su ID.")
async def obtener_tratamiento_por_id(
    id_tratamiento: int, 
    db: Session = Depends(get_db)
):
    gestion_tratamientos = GestionTratamientos(db)
    try:
        tratamiento = gestion_tratamientos.buscar_tratamiento_por_id(id_tratamiento)
        if not tratamiento:
            raise HTTPException(status_code=404, detail="Tratamiento no encontrado")
        return TratamientoResponse.model_validate(tratamiento)
    except Exception as e:
        logger.error(f"Error al obtener tratamiento por ID {id_tratamiento}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
