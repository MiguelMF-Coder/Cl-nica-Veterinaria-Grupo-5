import os
import logging
from sqlalchemy import inspect
from clinica.dbconfig import engine, Base, SessionLocal
from clinica.models import *
from datetime import datetime
from clinica.services.gestion_clientes import GestionClientes
from clinica.services.gestion_de_citas import GestionCitas
from clinica.services.gestion_mascotas import GestionMascotas
from clinica.services.gestion_tratamiento import GestionTratamientos
import json

# Configurar el logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Crear un manejador de consola y establecer el nivel
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formateador
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Añadir el manejador al logger
logger.addHandler(console_handler)

# Ruta base del proyecto (raíz del proyecto)
RUTA_BASE = os.path.dirname(os.path.abspath(__file__))  # Ruta de 'clinica'
PROYECTO_BASE = os.path.dirname(RUTA_BASE)  # Ruta de la raíz del proyecto

# Ruta a la carpeta 'data' para los JSON
RUTA_DATA = os.path.join(RUTA_BASE, "data")

# Ruta para la base de datos en la raíz del proyecto
DATABASE_PATH = os.path.join(PROYECTO_BASE, "clinica_db.sqlite")

# Verificar las rutas
print(f"Base de datos: {DATABASE_PATH}")
print(f"Carpeta de datos: {RUTA_DATA}")

# Asegurarnos de que el directorio de la base de datos exista
if not os.path.exists(PROYECTO_BASE):
    print("Error: El directorio raíz del proyecto no existe.")
else:
    print("El directorio raíz del proyecto existe.")

# Crear tablas si no existen
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if tables:
            print("Tablas creadas exitosamente:", tables)
        else:
            print("No se pudieron crear las tablas. Verifica la configuración.")
    except Exception as e:
        print(f"Error al crear las tablas: {e}")

# Función para cargar JSON
def cargar_json(ruta_json):
    if not os.path.exists(ruta_json):
        print(f"Error: el archivo {ruta_json} no existe.")
        return []
    try:
        with open(ruta_json, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON en {ruta_json}: {e}")
        return []

# Función genérica para cargar datos
def cargar_datos(session, modelo, datos, clave_primaria):
    for item in datos:
        try:
            # Manejo específico para fechas
            if modelo == Cita and "fecha" in item:
                item["fecha"] = datetime.strptime(item["fecha"], "%Y-%m-%d %H:%M:%S")
            
            filtro = {clave_primaria: item[clave_primaria]}
            registro_existente = session.query(modelo).filter_by(**filtro).first()
            if registro_existente:
                for key, value in item.items():
                    setattr(registro_existente, key, value)
                print(f"Registro actualizado: {item[clave_primaria]}")
            else:
                nuevo_registro = modelo(**item)
                session.add(nuevo_registro)
                print(f"Registro añadido: {item[clave_primaria]}")
        except Exception as e:
            print(f"Error al procesar el registro {item}: {e}")
    session.commit()


# Función para cargar todos los datos
def cargar_todos_los_datos():
    session = SessionLocal()
    try:
        for modelo, archivo, clave in [
            (Cliente, "datos_clientes.json", "id_cliente"),
            (Mascota, "datos_mascotas.json", "id_mascota"),
            (Tratamiento, "datos_tratamientos.json", "id_tratamiento"),
            (Cita, "datos_citas.json", "id_cita"),
        ]:
            datos = cargar_json(os.path.join(RUTA_DATA, archivo))
            cargar_datos(session, modelo, datos, clave)
    except Exception as e:
        print(f"Error inesperado al cargar datos: {e}")
    finally:
        session.close()


import logging

# Configurar el logger
logging.basicConfig(
    filename="exportacion_datos.log",  # Archivo donde se almacenarán los logs
    level=logging.INFO,                # Nivel de registro: INFO para registrar eventos generales
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def exportar_todos_json():
    """Exporta todos los datos a archivos JSON individuales."""
    try:
        # Crear una sesión de base de datos
        db_session = SessionLocal()

        # Instanciar las clases 
        gestion_clientes = GestionClientes(db_session)
        gestion_mascotas = GestionMascotas(db_session)
        gestion_citas = GestionCitas(db_session)
        gestion_tratamientos = GestionTratamientos(db_session)

        # Llamar a los métodos de exportación de cada clase
        logger.info("Iniciando exportación de clientes...")
        gestion_clientes.exportar_clientes_a_json(os.path.join(RUTA_DATA, "datos_clientes.json"))
        logger.info("Exportación de clientes completada exitosamente.")

        logger.info("Iniciando exportación de mascotas...")
        gestion_mascotas.exportar_mascotas_a_json(os.path.join(RUTA_DATA, "datos_mascotas.json"))
        logger.info("Exportación de mascotas completada exitosamente.")

        logger.info("Iniciando exportación de citas...")
        gestion_citas.exportar_citas_a_json(os.path.join(RUTA_DATA, "datos_citas.json"))
        logger.info("Exportación de citas completada exitosamente.")

        logger.info("Iniciando exportación de tratamientos...")
        gestion_tratamientos.exportar_tratamientos_a_json(os.path.join(RUTA_DATA, "datos_tratamientos.json"))
        logger.info("Exportación de tratamientos completada exitosamente.")

        # Cerrar la sesión de base de datos
        db_session.close()

        logger.info("Todas las exportaciones fueron completadas con éxito.")
        return True

    except Exception as e:
        logger.error(f"Error al exportar los datos: {str(e)}", exc_info=True)
        return False



if __name__ == "__main__":
    # Verificar si la base de datos existe
    if not os.path.exists(DATABASE_PATH):
        print("Base de datos no encontrada. Creando tablas...")
        create_tables()
    else:
        print("Base de datos encontrada. Conectando...")

    # Cargar datos
    cargar_todos_los_datos()
