import os
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from clinica.services.gestion_clientes import GestionClientes
from clinica.dbconfig import SessionLocal
from clinica_api.schemas import ClienteCreate, ClienteUpdate, ClienteResponse
from typing import List, Optional
import logging

# Configuramos el logging para mejor trazabilidad
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/clientes",  # Añadimos prefix para mantener consistencia con otros routers
    tags=["Clientes"],   # Añadimos tags para mejor documentación en Swagger
    responses={404: {"description": "Cliente no encontrado"},
              500: {"description": "Error interno del servidor"}}
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
            summary="Exportar clientes a JSON",
            description="Exporta todos los clientes de la base de datos a un archivo JSON.")
async def exportar_clientes(db: Session = Depends(get_db)):
    gestion_clientes = GestionClientes(db)
    try:
        ruta_exportada = os.path.join(os.getcwd(), 'clinica/data/tabla_clientes.json')
        gestion_clientes.exportar_clientes_a_json(ruta_json=ruta_exportada)
        logger.info(f"Clientes exportados exitosamente a {ruta_exportada}")
        return {
            "message": "Clientes exportados exitosamente",
            "ruta": ruta_exportada
        }
    except Exception as e:
        logger.error(f"Error al exportar clientes: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al exportar clientes: {str(e)}"
        )

@router.post("/", 
            response_model=ClienteResponse,
            status_code=201,  # Cambiamos a 201 Created para seguir convenciones REST
            summary="Registrar nuevo cliente",
            description="Crea un nuevo cliente en el sistema.")
async def registrar_cliente(
    cliente: ClienteCreate, 
    db: Session = Depends(get_db)
):
    gestion_clientes = GestionClientes(db)
    try:
        # Convertimos explícitamente el teléfono a string para evitar problemas de tipo
        cliente_data = cliente.model_dump()
        cliente_data['telefono'] = str(cliente_data['telefono'])
        
        resultado = gestion_clientes.registrar_cliente(cliente_data)
        if isinstance(resultado, dict) and "error" in resultado:
            raise HTTPException(status_code=400, detail=resultado["error"])
            
        logger.info(f"Cliente registrado exitosamente: {resultado.id_cliente}")
        return ClienteResponse.model_validate(resultado)
    except ValueError as ve:
        logger.error(f"Error de validación: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error al registrar cliente: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al registrar cliente: {str(e)}"
        )

@router.put("/{id_cliente}", 
           response_model=ClienteResponse,
           summary="Modificar cliente existente",
           description="Actualiza los datos de un cliente existente.")
async def modificar_cliente(
    id_cliente: int, 
    cliente: ClienteUpdate, 
    db: Session = Depends(get_db)
):
    gestion_clientes = GestionClientes(db)
    try:
        cliente_data = cliente.model_dump(exclude_unset=True)
        if 'telefono' in cliente_data:
            cliente_data['telefono'] = str(cliente_data['telefono'])
            
        resultado = gestion_clientes.modificar_cliente(id_cliente, cliente_data)
        if not resultado:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
            
        logger.info(f"Cliente {id_cliente} modificado exitosamente")
        return ClienteResponse.model_validate(resultado)
    except Exception as e:
        logger.error(f"Error al modificar cliente {id_cliente}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al modificar cliente: {str(e)}"
        )

@router.get("/", 
           response_model=List[ClienteResponse],
           summary="Listar todos los clientes",
           description="Obtiene una lista de todos los clientes registrados.")
async def listar_clientes(db: Session = Depends(get_db)):
    gestion_clientes = GestionClientes(db)
    try:
        clientes = gestion_clientes.listar_clientes()
        if not clientes:
            logger.warning("No se encontraron clientes registrados")
            return []
        return [ClienteResponse.model_validate(cliente) for cliente in clientes]
    except Exception as e:
        logger.error(f"Error al listar clientes: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al listar clientes: {str(e)}"
        )

@router.get("/buscar", 
           response_model=List[ClienteResponse],
           summary="Buscar clientes",
           description="Busca clientes por nombre o DNI.")
async def buscar_clientes(
    nombre: Optional[str] = Query(None, description="Nombre del cliente"),
    dni: Optional[str] = Query(None, description="DNI del cliente"),
    db: Session = Depends(get_db)
):
    gestion_clientes = GestionClientes(db)
    try:
        if dni:
            cliente = gestion_clientes.buscar_cliente(dni)
            return [ClienteResponse.model_validate(cliente)] if cliente else []
        elif nombre:
            clientes = gestion_clientes.buscar_cliente_por_nombre(nombre)
            return [ClienteResponse.model_validate(cliente) for cliente in clientes]
        else:
            raise HTTPException(
                status_code=400, 
                detail="Debe proporcionar al menos un criterio de búsqueda"
            )
    except Exception as e:
        logger.error(f"Error en búsqueda de clientes: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error en búsqueda de clientes: {str(e)}"
        )

@router.delete("/{id_cliente}",
              response_model=dict,
              summary="Eliminar cliente",
              description="Elimina un cliente del sistema.")
async def eliminar_cliente(id_cliente: int, db: Session = Depends(get_db)):
    gestion_clientes = GestionClientes(db)
    try:
        resultado = gestion_clientes.eliminar_cliente(id_cliente)
        if isinstance(resultado, dict) and "error" in resultado:
            raise HTTPException(status_code=404, detail=resultado["error"])
            
        logger.info(f"Cliente {id_cliente} eliminado exitosamente")
        return {"message": "Cliente eliminado exitosamente"}
    except Exception as e:
        logger.error(f"Error al eliminar cliente {id_cliente}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error al eliminar cliente: {str(e)}"
        )