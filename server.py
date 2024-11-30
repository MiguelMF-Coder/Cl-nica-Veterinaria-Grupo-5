from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from clinica.dbconfig import Base, engine, SessionLocal
from clinica_api.routers import clientes, citas, mascotas, tratamientos, exportaciones
from clinica.models import Cliente
from clinica.database import (
    cargar_todos_los_datos, 
    create_tables, 
    DATABASE_PATH, 
    RUTA_DATA
)
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

# Configuración del logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api.log')
    ]
)

logger = logging.getLogger(__name__)

def init_db():
    """Inicializa la base de datos y carga los datos iniciales de forma síncrona."""
    try:
        logger.info(f"Verificando base de datos en: {DATABASE_PATH}")
        
        # Verificar si el directorio de la base de datos existe
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        
        # Verificar si la base de datos existe
        if not os.path.exists(DATABASE_PATH):
            logger.info("Base de datos no encontrada. Creando nueva base de datos...")
            create_tables()
            logger.info("Estructura de base de datos creada exitosamente")
            
            # Verificar si existen los archivos JSON necesarios
            json_files = ["datos_clientes.json", "datos_mascotas.json", 
                         "datos_tratamientos.json", "datos_citas.json"]
            for json_file in json_files:
                json_path = os.path.join(RUTA_DATA, json_file)
                if not os.path.exists(json_path):
                    logger.warning(f"Archivo {json_file} no encontrado en {RUTA_DATA}")
                    return
            
            logger.info("Cargando datos iniciales...")
            cargar_todos_los_datos()
            logger.info("Datos iniciales cargados exitosamente")
        else:
            logger.info("Base de datos existente encontrada")
            
            # Verificar si hay datos
            db = SessionLocal()
            try:
                if not db.query(Cliente).first():
                    logger.info("Base de datos vacía. Cargando datos iniciales...")
                    cargar_todos_los_datos()
                    logger.info("Datos iniciales cargados exitosamente")
                else:
                    logger.info("Base de datos ya contiene datos")
            finally:
                db.close()

    except Exception as e:
        logger.error(f"Error durante la inicialización: {str(e)}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación."""
    logger.info("Iniciando la aplicación...")
    try:
        # Llamada a la función de inicialización síncrona
        init_db()
        yield
    except Exception as e:
        logger.error(f"Error durante la inicialización de la aplicación: {str(e)}")
        raise
    finally:
        logger.info("Cerrando la aplicación...")

# Instancia de FastAPI
app = FastAPI(
    title="API de Gestión de Clínica Veterinaria",
    description="Una API para gestionar clientes, mascotas, citas, productos y tratamientos en una clínica veterinaria.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# [Resto del código se mantiene igual...]

def get_db():
    """Proporciona una sesión de base de datos para las operaciones."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Registro de routers
app.include_router(clientes.router)
app.include_router(mascotas.router)
app.include_router(citas.router)
app.include_router(tratamientos.router)
app.include_router(exportaciones.router, prefix="/api")

@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz para verificar que la API está funcionando."""
    return {
        "message": "Bienvenido a la API de la Clínica Veterinaria",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/debug/routes", tags=["Debug"])
async def debug_routes():
    """Endpoint para depuración que muestra todas las rutas registradas."""
    return [
        {
            "path": route.path,
            "name": route.name,
            "methods": route.methods
        }
        for route in app.routes
    ]

@app.get("/health", tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """Verificación completa del estado de la aplicación."""
    try:
        db.execute("SELECT 1")
        
        inspector = inspect(engine)
        required_tables = {"cliente", "mascota", "cita", "tratamiento", "producto"}
        existing_tables = set(inspector.get_table_names())
        missing_tables = required_tables - existing_tables

        if missing_tables:
            return {
                "status": "warning",
                "database": "connected",
                "missing_tables": list(missing_tables)
            }

        return {
            "status": "healthy",
            "database": "connected",
            "tables": list(existing_tables)
        }
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Manejadores de excepciones
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Maneja errores específicos de SQLAlchemy."""
    logger.error(f"Error de base de datos: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error en la base de datos",
            "type": exc.__class__.__name__,
            "error": str(exc)
        }
    )

@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """Maneja errores de integridad de datos."""
    logger.error(f"Error de integridad: {str(exc)}")
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Error de integridad en los datos",
            "type": "IntegrityError",
            "error": str(exc)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Maneja cualquier excepción no capturada."""
    logger.error(f"Error no manejado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "type": exc.__class__.__name__,
            "error": str(exc)
        }
    )