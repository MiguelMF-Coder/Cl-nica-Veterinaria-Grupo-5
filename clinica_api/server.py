from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from clinica.dbconfig import Base, engine, SessionLocal
from clinica_api.routers import clientes, citas, mascotas, tratamientos
import logging

logging.basicConfig(level=logging.DEBUG)


app = FastAPI(
    title="API de Gestión de Clínica Veterinaria",
    description="Una API para gestionar clientes, mascotas, citas, productos y tratamientos en una clínica veterinaria.",
    version="1.0.0",
)

def initialize_database():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if not tables:
        print("No se encontraron tablas en la base de datos. Creándolas ahora...")
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas exitosamente.")
    else:
        print("Tablas ya existentes en la base de datos:", tables)

initialize_database()

# Dependencia de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Incluir routers de cada módulo
app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
app.include_router(mascotas.router, prefix="/mascotas", tags=["Mascotas"])
app.include_router(citas.router, prefix="/citas", tags=["Citas"])
app.include_router(tratamientos.router, prefix="/tratamientos", tags=["Tratamientos"])

# Ruta raíz para verificar que la API está funcionando
@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de la Clínica Veterinaria"}

# Endpoint de estado
@app.get("/status")
async def status(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "Base de datos conectada y operativa"}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Error de conexión con la base de datos")

# Manejo de excepciones de SQLAlchemy
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": "Error de la base de datos", "error": str(exc)}
    )

# Manejo de excepciones de integridad (duplicados, restricciones de clave)
@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"detail": "Conflicto de integridad: Duplicado o restricción violada", "error": str(exc)}
    )

# Manejo de excepciones generales
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno en el servidor", "error": str(exc)}
    )
