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
import tempfile
import shutil
from starlette.background import BackgroundTask
import logging
from datetime import datetime
import time

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

@router.get("/factura/generar/{id_tratamiento}",
            response_class=FileResponse,
            summary="Generar factura PDF",
            description="Genera una factura en formato PDF para un tratamiento")
async def generar_factura(id_tratamiento: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Generando factura PDF para tratamiento ID: {id_tratamiento}")
        
        # Obtener los datos necesarios
        tratamiento = db.query(Tratamiento).filter_by(id_tratamiento=id_tratamiento).first()
        if not tratamiento:
            raise HTTPException(status_code=404, detail="Tratamiento no encontrado")

        cita = db.query(Cita).filter_by(id_tratamiento=id_tratamiento).first()
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        cliente = db.query(Cliente).filter_by(id_cliente=cita.id_cliente).first()
        mascota = db.query(Mascota).filter_by(id_mascota=cita.id_mascota).first()
        
        if not cliente or not mascota:
            raise HTTPException(status_code=404, detail="Cliente o mascota no encontrados")

        # Crear directorio temporal
        temp_dir = tempfile.gettempdir()
        pdf_filename = f"factura_{id_tratamiento}_{int(time.time())}.pdf"
        pdf_path = os.path.join(temp_dir, pdf_filename)
        
        logger.info(f"Generando PDF en: {pdf_path}")

        # Generar PDF
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter

        # Encabezado
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, height - 50, "UFVVet Clínica Veterinaria")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 70, "Calle de la Mascota Feliz, 123")
        c.drawString(50, height - 85, "28223 Madrid")
        c.drawString(50, height - 100, "Tel: +34 123 456 789")

        # Información de la factura
        c.setFont("Helvetica-Bold", 16)
        c.drawString(400, height - 50, "FACTURA")
        
        c.setFont("Helvetica", 12)
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        c.drawString(400, height - 70, f"Fecha: {fecha_actual}")
        c.drawString(400, height - 85, f"Nº Factura: {cita.id_cita}")

        # Información del cliente
        c.line(50, height - 120, width - 50, height - 120)
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 150, "Datos del Cliente")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 170, f"Nombre: {cliente.nombre_cliente}")
        c.drawString(50, height - 185, f"DNI: {cliente.dni}")
        c.drawString(50, height - 200, f"Dirección: {cliente.direccion}")
        c.drawString(50, height - 215, f"Teléfono: {cliente.telefono}")

        # Información de la mascota
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 245, "Datos de la Mascota")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 265, f"Nombre: {mascota.nombre_mascota}")
        c.drawString(50, height - 280, f"Raza: {mascota.raza}")
        c.drawString(50, height - 295, f"Edad: {mascota.edad} años")

        # Detalles del tratamiento
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 325, "Detalles del Tratamiento")
        
        # Cabecera de la tabla
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 345, "Descripción")
        c.drawString(400, height - 345, "Precio")
        
        c.line(50, height - 350, width - 50, height - 350)
        
        # Contenido del tratamiento
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 370, tratamiento.nombre_tratamiento)
        c.drawString(50, height - 385, tratamiento.descripcion[:50] + "..." if len(tratamiento.descripcion) > 50 else tratamiento.descripcion)
        c.drawRightString(500, height - 370, f"{tratamiento.precio:.2f} €")

        # Línea total
        c.line(50, height - 410, width - 50, height - 410)
        
        # Total
        c.setFont("Helvetica-Bold", 14)
        c.drawString(350, height - 430, "Total:")
        c.drawRightString(500, height - 430, f"{tratamiento.precio:.2f} €")

        # Método de pago
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 460, f"Método de pago: {cita.metodo_pago}")

        # Pie de página
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, 50, "Gracias por confiar en UFVVet Clínica Veterinaria")
        c.drawString(50, 35, "Este documento sirve como comprobante de pago")

        logger.info(f"Intentando guardar archivo PDF en: {pdf_path}")
        c.save()
     # Verificar que el archivo se creó correctamente
        if not os.path.exists(pdf_path):
            logger.error(f"No se pudo generar el archivo PDF en {pdf_path}")
            raise HTTPException(status_code=500, detail="Error al generar el PDF")

        file_size = os.path.getsize(pdf_path)
        logger.info(f"PDF generado correctamente. Tamaño: {file_size} bytes")

        def cleanup():
            try:
                os.unlink(pdf_path)
                logger.info(f"Archivo temporal eliminado: {pdf_path}")
            except Exception as e:
                logger.error(f"Error al eliminar archivo temporal: {str(e)}")

        return FileResponse(
            path=pdf_path,
            filename=f"factura_{id_tratamiento}.pdf",
            media_type="application/pdf",
            background=BackgroundTask(cleanup)
        )

    except Exception as e:
        logger.error(f"Error al generar factura: {str(e)}")
        # Intentar limpiar el archivo si existe
        if 'pdf_path' in locals() and os.path.exists(pdf_path):
            try:
                os.unlink(pdf_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))