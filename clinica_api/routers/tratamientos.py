import os
from fastapi import APIRouter, Depends, HTTPException
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

from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/exportar", response_model=dict)
def exportar_tratamientos_a_json(db: Session = Depends(get_db)):
    gestion_tratamientos = GestionTratamientos(db)
    try:
        ruta_exportada = os.path.join(os.getcwd(), 'clinica/data/tabla_tratamientos.json')
        gestion_tratamientos.exportar_tratamientos_a_json(ruta_json=ruta_exportada)
        return {"message": f"Tratamientos exportados a {ruta_exportada} exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar tratamientos a JSON: {str(e)}")

# Endpoint para registrar un tratamiento
@router.post("/", response_model=TratamientoResponse)
def registrar_tratamiento(tratamiento: TratamientoCreate, db: Session = Depends(get_db)):
    gestion_tratamientos = GestionTratamientos(db)
    try:
        resultado = gestion_tratamientos.registrar_tratamiento(tratamiento.model_dump())
        if isinstance(resultado, str) and "Error" in resultado:
            raise HTTPException(status_code=400, detail=resultado)
        # Asegúrate de devolver una instancia de Tratamiento
        return TratamientoResponse.model_validate(resultado)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


# Endpoint para dar de baja un tratamiento
@router.delete("/{nombre_tratamiento}")
def dar_baja_tratamiento(nombre_tratamiento: str, db: Session = Depends(get_db)):
    try:
        gestion_tratamientos = GestionTratamientos(db)
        resultado = gestion_tratamientos.dar_baja_tratamiento(nombre_tratamiento)
        if "Error" in resultado:
            raise HTTPException(status_code=404, detail=resultado)
        return {"message": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint para modificar un tratamiento
@router.put("/{id_tratamiento}", response_model=TratamientoResponse)
def modificar_tratamiento(id_tratamiento: int, tratamiento: TratamientoUpdate, db: Session = Depends(get_db)):
    try:
        gestion_tratamientos = GestionTratamientos(db)
        resultado = gestion_tratamientos.modificar_tratamiento(id_tratamiento, tratamiento.model_dump(exclude_unset=True))
        if "Error" in resultado:
            raise HTTPException(status_code=404, detail=resultado)
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint para obtener datos de factura para un tratamiento
@router.get("/factura/{id_tratamiento}", response_model=dict)
def obtener_datos_factura(id_tratamiento: int, db: Session = Depends(get_db)):
    try:
        gestion_tratamientos = GestionTratamientos(db)
        datos_factura = gestion_tratamientos.obtener_datos_factura(id_tratamiento)
        if "error" in datos_factura:
            raise HTTPException(status_code=404, detail=datos_factura["error"])
        return datos_factura
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint para validar si el tratamiento está completado
@router.get("/validar/{id_tratamiento}", response_model=dict)
def validar_tratamiento_completado(id_tratamiento: int, db: Session = Depends(get_db)):
    try:
        gestion_tratamientos = GestionTratamientos(db)
        tratamiento = db.query(Tratamiento).filter_by(id_tratamiento=id_tratamiento).first()
        if not tratamiento:
            raise HTTPException(status_code=404, detail="Tratamiento no encontrado")

        resultado = gestion_tratamientos.validar_tratamiento_completado(tratamiento)
        if isinstance(resultado, dict) and "error" in resultado:
            raise HTTPException(status_code=400, detail=resultado["error"])
        return {"completado": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint para generar una factura en PDF
@router.get("/factura/generar/{id_tratamiento}", response_class=FileResponse)
async def generar_factura(id_tratamiento: int, db: Session = Depends(get_db)):
    try:
        # Obtener los datos necesarios
        tratamiento = db.query(Tratamiento).filter_by(id_tratamiento=id_tratamiento).first()
        if not tratamiento:
            raise HTTPException(status_code=404, detail="Tratamiento no encontrado")

        cita = db.query(Cita).filter_by(id_tratamiento=id_tratamiento).first()
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada para el tratamiento especificado")

        cliente = db.query(Cliente).filter_by(id_cliente=cita.id_cliente).first()
        mascota = db.query(Mascota).filter_by(id_mascota=cita.id_mascota).first()
        if not cliente or not mascota:
            raise HTTPException(status_code=404, detail="Cliente o mascota no encontrados")

        # Ruta para guardar el PDF temporalmente
        pdf_path = Path("factura.pdf")

        # Crear el PDF con un tamaño de página carta
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        width, height = letter

        # Encabezado del documento
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 80, "Clínica Veterinaria - Factura de Tratamiento")
        c.setFont("Helvetica", 10)
        c.drawString(100, height - 100, "Gracias por confiar en nuestra clínica.")

        # Separador
        c.setStrokeColor(colors.grey)
        c.setLineWidth(0.5)
        c.line(50, height - 110, width - 50, height - 110)

        # Información del Cliente
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 140, "Información del Cliente")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 160, f"Nombre: {cliente.nombre_cliente}")
        c.drawString(50, height - 175, f"DNI: {cliente.dni}")
        c.drawString(50, height - 190, f"Teléfono: {cliente.telefono}")
        c.drawString(50, height - 205, f"Dirección: {cliente.direccion}")

        # Información de la Mascota
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 235, "Información de la Mascota")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 255, f"Nombre: {mascota.nombre_mascota}")
        c.drawString(50, height - 270, f"Raza: {mascota.raza}")
        c.drawString(50, height - 285, f"Edad: {mascota.edad} años")
        c.drawString(50, height - 300, f"Afección: {mascota.afeccion if mascota.afeccion else 'Ninguna'}")

        # Información de la Cita
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 330, "Información de la Cita")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 350, f"Fecha: {cita.fecha.strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(50, height - 365, f"Descripción: {cita.descripcion}")

        # Información del Tratamiento
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 395, "Información del Tratamiento")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 415, f"Tratamiento: {tratamiento.nombre_tratamiento}")
        c.drawString(50, height - 430, f"Descripción: {tratamiento.descripcion}")
        c.drawString(50, height - 445, f"Precio: {tratamiento.precio} €")

        # Total y Agradecimiento
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height - 475, "Total a Pagar:")
        c.setFont("Helvetica", 10)
        c.drawString(150, height - 475, f"{tratamiento.precio} €")
        
        c.drawString(50, height - 495, "Gracias por confiar en nosotros. ¡Esperamos su próxima visita!")
        
        # Finalizar el PDF
        c.showPage()
        c.save()

        return FileResponse(path=pdf_path, filename="factura.pdf", media_type="application/pdf")

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
