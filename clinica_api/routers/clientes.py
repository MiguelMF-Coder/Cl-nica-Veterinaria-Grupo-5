import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from clinica.services.gestion_clientes import GestionClientes
from clinica.dbconfig import SessionLocal
from clinica_api.schemas import ClienteCreate, ClienteUpdate, ClienteResponse
from typing import List

router = APIRouter()

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint para exportar clientes a JSON
@router.post("/exportar", response_model=dict)
def exportar_clientes(db: Session = Depends(get_db)):
    gestion_clientes = GestionClientes(db)
    try:
        ruta_exportada = os.path.join(os.getcwd(), 'clinica/data/tabla_clientes.json')
        gestion_clientes.exportar_clientes_a_json(ruta_json=ruta_exportada)
        return {"message": f"Clientes exportados a {ruta_exportada} exitosamente"}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al exportar clientes a JSON.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# Endpoint para registrar un cliente
@router.post("/", response_model=ClienteResponse)
def registrar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    gestion_clientes = GestionClientes(db)
    try:
        resultado = gestion_clientes.registrar_cliente(cliente.model_dump())
        if isinstance(resultado, dict) and "error" in resultado:
            raise HTTPException(status_code=400, detail=resultado["error"])
        return ClienteResponse.model_validate(resultado)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al registrar el cliente en la base de datos.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# Endpoint para modificar un cliente
@router.put("/{id_cliente}", response_model=ClienteResponse)
def modificar_cliente(id_cliente: int, cliente: ClienteUpdate, db: Session = Depends(get_db)):
    gestion_clientes = GestionClientes(db)
    try:
        resultado = gestion_clientes.modificar_cliente(id_cliente, cliente.model_dump(exclude_unset=True))
        if isinstance(resultado, dict) and "error" in resultado:
            raise HTTPException(status_code=404, detail=resultado["error"])
        return ClienteResponse.model_validate(resultado)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al modificar el cliente en la base de datos.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# Endpoint para eliminar un cliente
@router.delete("/{id_cliente}", response_model=dict)
def eliminar_cliente(id_cliente: int, db: Session = Depends(get_db)):
    gestion_clientes = GestionClientes(db)
    try:
        resultado = gestion_clientes.eliminar_cliente(id_cliente)
        if isinstance(resultado, dict) and "error" in resultado:
            raise HTTPException(status_code=404, detail=resultado["error"])
        return {"message": resultado}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al eliminar el cliente de la base de datos.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# Endpoint para buscar un cliente por DNI
@router.get("/buscar/{dni}", response_model=ClienteResponse)
def buscar_cliente(dni: str, db: Session = Depends(get_db)):
    gestion_clientes = GestionClientes(db)
    try:
        cliente = gestion_clientes.buscar_cliente(dni)
        if cliente is None:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return ClienteResponse.model_validate(cliente)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al buscar el cliente en la base de datos.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# Endpoint para buscar un cliente por nombre y obtener mascotas asociadas
@router.get("/buscar_por_nombre/{nombre_cliente}", response_model=dict)
def buscar_cliente_por_nombre(nombre_cliente: str, db: Session = Depends(get_db)):
    gestion_clientes = GestionClientes(db)
    try:
        resultado = gestion_clientes.buscar_cliente_por_nombre(nombre_cliente)
        if resultado is None:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return resultado
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al buscar el cliente en la base de datos.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

# Endpoint para listar todos los clientes
@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(db: Session = Depends(get_db)):
    gestion_clientes = GestionClientes(db)
    try:
        clientes = gestion_clientes.listar_clientes()
        return [ClienteResponse.model_validate(cliente) for cliente in clientes]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error al listar los clientes de la base de datos.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
