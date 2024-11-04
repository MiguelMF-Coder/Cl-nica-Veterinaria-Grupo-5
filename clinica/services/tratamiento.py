import re  # Importamos la librería de expresiones regulares para validar entradas
from sqlalchemy.orm import Session
from clinica.models.tabla_tratamiento import Tratamiento  
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GestionTratamientos:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def dar_alta_tratamiento(self, tratamiento_data):
        try:
            # Verificar si el tratamiento ya existe en la base de datos
            tratamiento_existente = self.db_session.query(Tratamiento).filter_by(nombre_tratamiento=tratamiento_data['nombre_tratamiento']).first()
            if tratamiento_existente:
                logging.warning(f"El tratamiento '{tratamiento_data['nombre_tratamiento']}' ya está registrado.")
                print(f"Error: El tratamiento '{tratamiento_data['nombre_tratamiento']}' ya está registrado.")
                return

            # Crear una nueva instancia de tratamiento y agregarla a la base de datos
            nuevo_tratamiento = Tratamiento(**tratamiento_data)
            self.db_session.add(nuevo_tratamiento)
            self.db_session.commit()
            logging.info(f"Tratamiento '{tratamiento_data['nombre_tratamiento']}' dado de alta con éxito.")
            print(f"Tratamiento '{tratamiento_data['nombre_tratamiento']}' dado de alta con éxito.")
        
        except IntegrityError as ie:
            self.db_session.rollback()
            logging.error("Error de integridad al registrar el tratamiento: %s", ie)
            print("Error: No se pudo registrar el tratamiento debido a un problema de integridad.")
        
        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al registrar el tratamiento: %s", sae)
            print(f"Error: Ocurrió un problema con la base de datos: {sae}")
        
        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al registrar el tratamiento: %s", e)
            print(f"Ocurrió un error inesperado al dar de alta el tratamiento: {e}")

    def dar_baja_tratamiento(self, nombre_tratamiento):
        try:
            tratamiento = self.db_session.query(Tratamiento).filter_by(nombre_tratamiento=nombre_tratamiento).first()
            if tratamiento:
                self.db_session.delete(tratamiento)
                self.db_session.commit()
                logging.info(f"Tratamiento '{nombre_tratamiento}' dado de baja con éxito.")
                print(f"Tratamiento '{nombre_tratamiento}' dado de baja con éxito.")
            else:
                logging.warning(f"Tratamiento '{nombre_tratamiento}' no encontrado.")
                print(f"Error: No se encontró el tratamiento '{nombre_tratamiento}'.")
        
        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al dar de baja el tratamiento: %s", sae)
            print(f"Error al dar de baja el tratamiento: {sae}")
        
        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al dar de baja el tratamiento: %s", e)
            print(f"Ocurrió un error inesperado al dar de baja el tratamiento: {e}")

    def modificar_tratamiento(self, id_tratamiento, nuevos_datos):
        try:
            tratamiento = self.db_session.query(Tratamiento).filter_by(id_tratamiento=id_tratamiento).first()
            if tratamiento:
                # Actualizar los atributos del tratamiento con los nuevos datos
                for key, value in nuevos_datos.items():
                    if hasattr(tratamiento, key):
                        setattr(tratamiento, key, value)
                
                self.db_session.commit()
                logging.info(f"Tratamiento con ID '{id_tratamiento}' modificado con éxito.")
                print(f"Tratamiento con ID '{id_tratamiento}' modificado con éxito.")
            else:
                logging.warning(f"No se encontró el tratamiento con ID '{id_tratamiento}'.")
                print(f"Error: No se encontró el tratamiento con ID '{id_tratamiento}'.")
        
        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al modificar el tratamiento: %s", sae)
            print(f"Error al modificar el tratamiento: {sae}")
        
        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al modificar el tratamiento: %s", e)
            print(f"Ocurrió un error inesperado al modificar el tratamiento: {e}")
