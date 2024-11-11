# Importaciones iniciales
import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from clinica.services.gestion_de_citas import GestionCitas  
from clinica.dbconfig import SessionLocal
from clinica_api.schemas import CitaCreate, CitaUpdate, CitaResponse  
from typing import List

# Definir el router con el prefijo /citas
router = APIRouter()

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint para exportar citas a JSON
@router.post("/exportar", response_model=dict)
def exportar_citas_a_json(db: Session = Depends(get_db)):
    gestion_citas = GestionCitas(db)
    try:
        ruta_exportada = os.path.join(os.getcwd(), 'clinica/data/tabla_citas.json')
        resultado = gestion_citas.exportar_citas_a_json(ruta_json=ruta_exportada)
        
        if isinstance(resultado, dict) and "error" in resultado:
            raise HTTPException(status_code=500, detail=resultado["error"])
        
        return {"message": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# Endpoint para registrar una nueva cita
@router.post("/", response_model=CitaResponse)
def registrar_cita(cita: CitaCreate, db: Session = Depends(get_db)):
    gestion_citas = GestionCitas(db)
    try:
        # `registrar_cita` devuelve un objeto Cita en caso de éxito
        nueva_cita = gestion_citas.registrar_cita(cita.model_dump())
        print("Resultado antes de validar en model_validate:", nueva_cita)
        return CitaResponse.model_validate(nueva_cita)
    
    except ValueError as ve:
        # Para errores específicos que puedan surgir en la lógica del negocio
        raise HTTPException(status_code=400, detail=str(ve))
    except SQLAlchemyError as sae:
        # Captura errores de la base de datos
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {str(sae)}")
    except Exception as e:
        # Captura cualquier otro error inesperado
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


# Endpoint para ver todas las citas
@router.get("/", response_model=List[CitaResponse])
def ver_todas_las_citas(db: Session = Depends(get_db)):
    gestion_citas = GestionCitas(db)
    try:
        citas = gestion_citas.ver_todas_las_citas()
        if isinstance(citas, str) and "Error" in citas:
            raise HTTPException(status_code=500, detail=citas)
        return [CitaResponse.model_validate(cita) for cita in citas]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# Endpoint para buscar una cita por ID de mascota y cliente
@router.get("/buscar/{id_mascota}/{id_cliente}", response_model=CitaResponse)
def buscar_cita(id_mascota: int, id_cliente: int, db: Session = Depends(get_db)):
    gestion_citas = GestionCitas(db)
    try:
        cita = gestion_citas.buscar_cita(id_mascota, id_cliente)
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        return CitaResponse.model_validate(cita)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# Endpoint para modificar una cita
@router.put("/{id_cita}", response_model=CitaResponse)
def modificar_cita(id_cita: int, cita: CitaUpdate, db: Session = Depends(get_db)):
    gestion_citas = GestionCitas(db)
    try:
        resultado = gestion_citas.modificar_cita(id_cita, cita.model_dump(exclude_unset=True))
        if isinstance(resultado, str) and "Error" in resultado:
            raise HTTPException(status_code=404, detail=resultado)
        return CitaResponse.model_validate(resultado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# Endpoint para cancelar una cita
@router.delete("/{id_cita}", response_model=dict)
def cancelar_cita(id_cita: int, db: Session = Depends(get_db)):
    gestion_citas = GestionCitas(db)
    try:
        resultado = gestion_citas.cancelar_cita(id_cita)
        if isinstance(resultado, str) and "Error" in resultado:
            raise HTTPException(status_code=404, detail=resultado)
        return {"message": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# Endpoint para finalizar una cita y establecer el método de pago
@router.put("/finalizar/{id_cita}", response_model=dict)
def finalizar_cita(id_cita: int, tratamientos_realizados: str, metodo_pago: str, db: Session = Depends(get_db)):
    gestion_citas = GestionCitas(db)
    try:
        resultado = gestion_citas.finalizar_cita(id_cita, tratamientos_realizados, metodo_pago)
        if isinstance(resultado, str) and "Error" in resultado:
            raise HTTPException(status_code=400, detail=resultado)
        return {"message": resultado}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
