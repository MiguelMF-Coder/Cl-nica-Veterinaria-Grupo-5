# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuramos la URL de la base de datos esto creara un archivo local con los datos
DATABASE_URL = "sqlite:///./clinica.db"

# Crear el motor de base de datos
engine = create_engine(DATABASE_URL, echo=True)

# Crear la sesión de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para definir los modelos
Base = declarative_base()
