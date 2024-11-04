import json
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError
from dbconfig import engine, Base, SessionLocal
from models.tabla_cliente import Cliente
from models.tabla_mascota import Mascota
from models.tabla_citas import Cita
from models.tabla_tratamiento import Tratamiento
from models.tabla_productos import Producto
from pathlib import Path
from datetime import datetime
import os

# Ruta a la carpeta 'data'
RUTA_BASE = Path(__file__).resolve().parent
RUTA_DATA = RUTA_BASE / 'data'

#Ruta a la carpeta bdd
DATABASE_PATH = os.path.abspath("clinica_db.sqlite")

def create_tables():
    try:
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        
        # Inspeccionar las tablas creadas
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if tables:
            print("Tablas en la base de datos:", tables)
            print("Tablas creadas exitosamente.")
        else:
            print("No se pudieron crear las tablas. Verifica la configuración.")
    except OperationalError as e:
        print("Error al conectar o crear la base de datos:", e)
    except Exception as e:
        print("Error inesperado:", e)

# Funciones para cargar datos desde archivos JSON
def cargar_clientes_desde_json(ruta_json):
    session = SessionLocal()
    with open(ruta_json, 'r', encoding='utf-8') as archivo:
        datos = json.load(archivo)
        for item in datos:
            cliente = Cliente(**item)
            session.add(cliente)
    session.commit()
    print("Clientes cargados exitosamente.")
    session.close()

def cargar_mascotas_desde_json(ruta_json):
    session = SessionLocal()
    with open(ruta_json, 'r', encoding='utf-8') as archivo:
        datos = json.load(archivo)
        for item in datos:
            mascota = Mascota(**item)
            session.add(mascota)
    session.commit()
    print("Mascotas cargadas exitosamente.")
    session.close()

def cargar_citas_desde_json(ruta_json):
    session = SessionLocal()
    with open(ruta_json, 'r', encoding='utf-8') as archivo:
        datos = json.load(archivo)
        for item in datos:
            if 'fecha' in item:
                item['fecha'] = datetime.strptime(item['fecha'], "%Y-%m-%d %H:%M:%S")
            cita = Cita(**item)
            session.add(cita)
    session.commit()
    print("Citas cargadas exitosamente.")
    session.close()

def cargar_tratamientos_desde_json(ruta_json):
    session = SessionLocal()
    with open(ruta_json, 'r', encoding='utf-8') as archivo:
        datos = json.load(archivo)
        for item in datos:
            tratamiento = Tratamiento(**item)
            session.add(tratamiento)
    session.commit()
    print("Tratamientos cargados exitosamente.")
    session.close()

def cargar_productos_desde_json(ruta_json):
    session = SessionLocal()
    with open(ruta_json, 'r', encoding='utf-8') as archivo:
        datos = json.load(archivo)
        for item in datos:
            producto = Producto(**item)
            session.add(producto)
    session.commit()
    print("Productos cargados exitosamente.")
    session.close()

if __name__ == "__main__":
    if not os.path.exists(DATABASE_PATH):
        create_tables()  # Crear las tablas antes de cargar los datos

cargar_clientes_desde_json(RUTA_DATA / 'datos_clientes.json')
cargar_mascotas_desde_json(RUTA_DATA / 'datos_mascotas.json')
cargar_tratamientos_desde_json(RUTA_DATA / 'datos_tratamientos.json')
cargar_productos_desde_json(RUTA_DATA / 'datos_productos.json')
cargar_citas_desde_json(RUTA_DATA / 'datos_citas.json')
