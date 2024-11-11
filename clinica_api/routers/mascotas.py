import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from clinica.services.gestion_mascotas import GestionMascotas
from clinica.dbconfig import SessionLocal
from clinica_api.schemas import MascotaCreate, MascotaUpdate, MascotaResponse
from typing import List

router = APIRouter()

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint para exportar mascotas a JSON
@router.post("/exportar", response_model=dict)
def exportar_mascotas(db: Session = Depends(get_db)):
    gestion_mascotas = GestionMascotas(db)
    try:
        ruta_exportada = os.path.abspath('clinica/data/tabla_mascotas.json')
        gestion_mascotas.exportar_mascotas_a_json(ruta_json=ruta_exportada)
        return {"message": f"Mascotas exportadas a {ruta_exportada} exitosamente"}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al exportar mascotas a JSON.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# Endpoint para registrar una mascota
@router.post("/", response_model=MascotaResponse)
def registrar_mascota(mascota: MascotaCreate, db: Session = Depends(get_db)):
    gestion_mascotas = GestionMascotas(db)
    try:
        # Aquí pasamos tanto el id_cliente como el resto de los datos de la mascota
        resultado = gestion_mascotas.registrar_mascota(mascota.id_cliente, mascota.model_dump())
        
        if isinstance(resultado, str) and "Error" in resultado:
            raise HTTPException(status_code=400, detail=resultado)
        
        return resultado
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al registrar la mascota en la base de datos.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


# Endpoint para modificar una mascota
@router.put("/{id_mascota}", response_model=MascotaResponse)
def modificar_mascota(id_mascota: int, mascota: MascotaUpdate, db: Session = Depends(get_db)):
    gestion_mascotas = GestionMascotas(db)
    try:
        resultado = gestion_mascotas.modificar_mascota(id_mascota, mascota.model_dump(exclude_unset=True))
        if isinstance(resultado, str) and "Error" in resultado:
            raise HTTPException(status_code=404, detail=resultado)
        return resultado
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al modificar la mascota en la base de datos.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# Endpoint para eliminar una mascota
@router.delete("/{id_mascota}")
def eliminar_mascota(id_mascota: int, db: Session = Depends(get_db)):
    gestion_mascotas = GestionMascotas(db)
    try:
        resultado = gestion_mascotas.eliminar_mascota(id_mascota)
        if isinstance(resultado, str) and "Error" in resultado:
            raise HTTPException(status_code=404, detail=resultado)
        return {"message": resultado}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al eliminar la mascota de la base de datos.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# Endpoint para listar todas las mascotas
@router.get("/", response_model=List[MascotaResponse])
def listar_mascotas(db: Session = Depends(get_db)):
    gestion_mascotas = GestionMascotas(db)
    try:
        return gestion_mascotas.listar_mascotas()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al listar las mascotas de la base de datos.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# Endpoint para buscar una mascota por nombre
@router.get("/buscar_por_nombre/{nombre_mascota}")
def buscar_mascota_por_nombre(nombre_mascota: str, db: Session = Depends(get_db)):
    gestion_mascotas = GestionMascotas(db)
    try:
        resultado = gestion_mascotas.buscar_mascota_por_nombre(nombre_mascota)
        if resultado is None:
            raise HTTPException(status_code=404, detail="Mascota no encontrada")
        return resultado
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al buscar la mascota en la base de datos.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# Endpoint para marcar una mascota como fallecida
@router.put("/fallecido/{id_cliente}/{nombre_mascota}")
def marcar_mascota_como_fallecido(id_cliente: int, nombre_mascota: str, db: Session = Depends(get_db)):
    gestion_mascotas = GestionMascotas(db)
    try:
        resultado = gestion_mascotas.marcar_mascota_como_fallecido(id_cliente, nombre_mascota)
        if isinstance(resultado, str) and "Error" in resultado:
            raise HTTPException(status_code=404, detail=resultado)
        return {"message": resultado}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al actualizar el estado de la mascota en la base de datos.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
