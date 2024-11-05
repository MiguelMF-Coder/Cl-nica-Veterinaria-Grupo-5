#database.py

import json
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError
from clinica.dbconfig import engine, Base, SessionLocal
from clinica.models import *
from pathlib import Path
from datetime import datetime
import os

# Ruta a la carpeta 'data'
RUTA_BASE = Path(__file__).resolve().parent
RUTA_DATA = RUTA_BASE / 'data'

#Ruta a la carpeta bdd
DATABASE_PATH = os.path.join(RUTA_BASE, "clinica_db.sqlite")

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
    if not os.path.exists(ruta_json):
        print(f"Error: el archivo {ruta_json} no existe.")
        return
    
    session = SessionLocal()
    try:
        with open(ruta_json, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
            for item in datos:
                try:
                    cliente_existente = session.query(Cliente).filter_by(id_cliente=item['id_cliente']).first()
                    if cliente_existente:
                        for key, value in item.items():
                            setattr(cliente_existente, key, value)
                        print(f"Cliente con id {item['id_cliente']} actualizado.")
                    else:
                        nuevo_cliente = Cliente(**item)
                        session.add(nuevo_cliente)
                        print(f"Cliente con id {item['id_cliente']} añadido.")
                except Exception as e:
                    print(f"Error al procesar cliente {item['id_cliente']}: {e}")
        
        session.commit()
        print("Clientes cargados y actualizados exitosamente.")
    except json.JSONDecodeError:
        print("Error: El archivo JSON no está bien formado.")
    except Exception as e:
        print(f"Error inesperado al cargar clientes: {e}")
        session.rollback()
    finally:
        session.close()

def cargar_mascotas_desde_json(ruta_json):
    if not os.path.exists(ruta_json):
        print(f"Error: el archivo {ruta_json} no existe.")
        return
    
    session = SessionLocal()
    try:
        with open(ruta_json, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
            for item in datos:
                try:
                    mascota_existente = session.query(Mascota).filter_by(id_mascota=item['id_mascota']).first()
                    if mascota_existente:
                        for key, value in item.items():
                            setattr(mascota_existente, key, value)
                        print(f"Mascota con id {item['id_mascota']} actualizada.")
                    else:
                        nueva_mascota = Mascota(**item)
                        session.add(nueva_mascota)
                        print(f"Mascota con id {item['id_mascota']} añadida.")
                except Exception as e:
                    print(f"Error al procesar mascota {item['id_mascota']}: {e}")
        
        session.commit()
        print("Mascotas cargadas y actualizadas exitosamente.")
    except json.JSONDecodeError:
        print("Error: El archivo JSON no está bien formado.")
    except Exception as e:
        print(f"Error inesperado al cargar mascotas: {e}")
        session.rollback()
    finally:
        session.close()

def cargar_citas_desde_json(ruta_json):
    if not os.path.exists(ruta_json):
        print(f"Error: el archivo {ruta_json} no existe.")
        return
    
    session = SessionLocal()
    try:
        with open(ruta_json, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
            for item in datos:
                try:
                    if 'fecha' in item:
                        item['fecha'] = datetime.strptime(item['fecha'], "%Y-%m-%d %H:%M:%S")
                    cita_existente = session.query(Cita).filter_by(id_cita=item['id_cita']).first()
                    if cita_existente:
                        for key, value in item.items():
                            setattr(cita_existente, key, value)
                        print(f"Cita con id {item['id_cita']} actualizada.")
                    else:
                        nueva_cita = Cita(**item)
                        session.add(nueva_cita)
                        print(f"Cita con id {item['id_cita']} añadida.")
                except Exception as e:
                    print(f"Error al procesar cita {item['id_cita']}: {e}")
        
        session.commit()
        print("Citas cargadas y actualizadas exitosamente.")
    except json.JSONDecodeError:
        print("Error: El archivo JSON no está bien formado.")
    except Exception as e:
        print(f"Error inesperado al cargar citas: {e}")
        session.rollback()
    finally:
        session.close()

def cargar_tratamientos_desde_json(ruta_json):
    if not os.path.exists(ruta_json):
        print(f"Error: el archivo {ruta_json} no existe.")
        return
    
    session = SessionLocal()
    try:
        with open(ruta_json, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
            for item in datos:
                try:
                    tratamiento_existente = session.query(Tratamiento).filter_by(id_tratamiento=item['id_tratamiento']).first()
                    if tratamiento_existente:
                        for key, value in item.items():
                            setattr(tratamiento_existente, key, value)
                        print(f"Tratamiento con id {item['id_tratamiento']} actualizado.")
                    else:
                        nuevo_tratamiento = Tratamiento(**item)
                        session.add(nuevo_tratamiento)
                        print(f"Tratamiento con id {item['id_tratamiento']} añadido.")
                except Exception as e:
                    print(f"Error al procesar tratamiento {item['id_tratamiento']}: {e}")
        
        session.commit()
        print("Tratamientos cargados y actualizados exitosamente.")
    except json.JSONDecodeError:
        print("Error: El archivo JSON no está bien formado.")
    except Exception as e:
        print(f"Error inesperado al cargar tratamientos: {e}")
        session.rollback()
    finally:
        session.close()

def cargar_productos_desde_json(ruta_json):
    if not os.path.exists(ruta_json):
        print(f"Error: el archivo {ruta_json} no existe.")
        return
    
    session = SessionLocal()
    try:
        with open(ruta_json, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
            for item in datos:
                try:
                    producto_existente = session.query(Producto).filter_by(id_producto=item['id_producto']).first()
                    if producto_existente:
                        for key, value in item.items():
                            setattr(producto_existente, key, value)
                        print(f"Producto con id {item['id_producto']} actualizado.")
                    else:
                        nuevo_producto = Producto(**item)
                        session.add(nuevo_producto)
                        print(f"Producto con id {item['id_producto']} añadido.")
                except Exception as e:
                    print(f"Error al procesar producto {item['id_producto']}: {e}")
        
        session.commit()
        print("Productos cargados y actualizados exitosamente.")
    except json.JSONDecodeError:
        print("Error: El archivo JSON no está bien formado.")
    except Exception as e:
        print(f"Error inesperado al cargar productos: {e}")
        session.rollback()
    finally:
        session.close()



if __name__ == "__main__":
    if not os.path.exists(DATABASE_PATH):
        create_tables()  # Crear las tablas antes de cargar los datos

cargar_clientes_desde_json(RUTA_DATA / 'datos_clientes.json')
cargar_mascotas_desde_json(RUTA_DATA / 'datos_mascotas.json')
cargar_tratamientos_desde_json(RUTA_DATA / 'datos_tratamientos.json')
cargar_productos_desde_json(RUTA_DATA / 'datos_productos.json')
cargar_citas_desde_json(RUTA_DATA / 'datos_citas.json')
