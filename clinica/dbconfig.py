import os
import logging
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError


# Configurar logging para SQLAlchemy
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    stream=sys.stdout,
)

# Configurar el logger específico de SQLAlchemy
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

# Configuración de la base de datos
DATABASE_PATH = os.path.abspath("clinica_db.sqlite")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Imprimir la ruta completa para verificar
print(f"Ruta completa de la base de datos: {DATABASE_PATH}")

# Crear el motor de la base de datos
try:
    engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True, connect_args={"check_same_thread": False})
except OperationalError as e:
    print(f"Error al crear el motor de la base de datos: {e}")
    exit(1)

# Crear la sesión de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para definir los modelos de datos
Base = declarative_base()
