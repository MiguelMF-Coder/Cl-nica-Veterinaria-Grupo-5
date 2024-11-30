from fastapi import APIRouter, HTTPException
from clinica.database import exportar_todos_json

router = APIRouter()

@router.post("/exportar_todos_json", tags=["Exportaciones"])
async def exportar_datos():
    """Endpoint para exportar todos los datos a archivos JSON"""
    try:
        exito = exportar_todos_json()
        if exito:
            return {"mensaje": "Exportación realizada con éxito"}
        else:
            raise HTTPException(status_code=500, detail="Error al exportar los datos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar los datos: {str(e)}")
