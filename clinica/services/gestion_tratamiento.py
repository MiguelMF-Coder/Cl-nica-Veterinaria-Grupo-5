# gestion_tratamiento.py

import os
import json
from sqlalchemy.orm import Session
from clinica.models import Tratamiento,Cita,Cliente,Mascota
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GestionTratamientos:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def exportar_tratamientos_a_json(self, ruta_json=None):
        """Exporta los tratamientos a un archivo JSON."""
        if ruta_json is None:
            ruta_json = os.path.join(os.getcwd(), 'clinica/data/tabla_tratamientos.json')

        # Verifica que el directorio exista y créalo si no existe
        directorio = os.path.dirname(ruta_json)
        if not os.path.exists(directorio):
            os.makedirs(directorio)
        
        try:
            tratamientos = self.db_session.query(Tratamiento).all()
            datos = [tratamiento.to_dict() for tratamiento in tratamientos]  # Asegúrate de que `to_dict()` esté implementado en `Tratamiento`
            
            with open(ruta_json, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=4)
            logging.info(f"Tratamientos exportados a {ruta_json} exitosamente.")
            return f"Tratamientos exportados a {ruta_json} exitosamente."
        except SQLAlchemyError as e:
            logging.error(f"Error al exportar tratamientos a JSON: {e}")
            return {"error": f"Error al exportar tratamientos a JSON: {e}"}
        except Exception as e:
            logging.error(f"Error inesperado al exportar tratamientos a JSON: {e}")
            return {"error": f"Error inesperado al exportar tratamientos a JSON: {e}"}

    def dar_alta_tratamiento(self, tratamiento_data):
        try:
            # Verificar si el tratamiento ya existe en la base de datos
            tratamiento_existente = self.db_session.query(Tratamiento).filter_by(nombre_tratamiento=tratamiento_data['nombre_tratamiento']).first()
            if tratamiento_existente:
                logging.warning(f"El tratamiento '{tratamiento_data['nombre_tratamiento']}' ya está registrado.")
                return f"Error: El tratamiento '{tratamiento_data['nombre_tratamiento']}' ya está registrado."

            # Crear una nueva instancia de tratamiento y agregarla a la base de datos
            nuevo_tratamiento = Tratamiento(**tratamiento_data)
            self.db_session.add(nuevo_tratamiento)
            self.db_session.commit()
            self.db_session.refresh(nuevo_tratamiento)  # Actualiza el objeto para que los datos sean accesibles
            
            logging.info(f"Tratamiento '{tratamiento_data['nombre_tratamiento']}' dado de alta con éxito.")
            
            # Devolver el objeto `Tratamiento` creado
            return nuevo_tratamiento

        except IntegrityError as ie:
            self.db_session.rollback()
            logging.error("Error de integridad al registrar el tratamiento: %s", ie)
            raise ValueError("Error: No se pudo registrar el tratamiento debido a un problema de integridad.")

        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al registrar el tratamiento: %s", sae)
            raise RuntimeError(f"Error: Ocurrió un problema con la base de datos: {sae}")


    def dar_baja_tratamiento(self, nombre_tratamiento):
        try:
            tratamiento = self.db_session.query(Tratamiento).filter_by(nombre_tratamiento=nombre_tratamiento).first()
            if tratamiento:
                self.db_session.delete(tratamiento)
                self.db_session.commit()
                logging.info(f"Tratamiento '{nombre_tratamiento}' dado de baja con éxito.")
                return f"Tratamiento '{nombre_tratamiento}' dado de baja con éxito."
            else:
                logging.warning(f"Tratamiento '{nombre_tratamiento}' no encontrado.")
                return f"Error: No se encontró el tratamiento '{nombre_tratamiento}'."
        
        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al dar de baja el tratamiento: %s", sae)
            return f"Error al dar de baja el tratamiento: {sae}"
        
        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al dar de baja el tratamiento: %s", e)
            return f"Ocurrió un error inesperado al dar de baja el tratamiento: {e}"

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
                return f"Tratamiento con ID '{id_tratamiento}' modificado con éxito."
            else:
                logging.warning(f"No se encontró el tratamiento con ID '{id_tratamiento}'.")
                return f"Error: No se encontró el tratamiento con ID '{id_tratamiento}'."
        
        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al modificar el tratamiento: %s", sae)
            return f"Error al modificar el tratamiento: {sae}"
        
        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al modificar el tratamiento: %s", e)
            return f"Ocurrió un error inesperado al modificar el tratamiento: {e}"
        
    def obtener_datos_factura(self, id_tratamiento: int):
        """
        Recupera la información completa para generar la factura de un tratamiento.
        Incluye los datos del cliente, mascota, cita y tratamiento.
        Maneja errores específicos y excepciones de base de datos.
        """
        try:
            # Obtener el tratamiento
            tratamiento = self.db_session.query(Tratamiento).filter_by(id_tratamiento=id_tratamiento).first()
            if not tratamiento:
                logging.error(f"Tratamiento con ID {id_tratamiento} no encontrado.")
                return {"error": "Tratamiento no encontrado"}
            
            # Obtener la cita relacionada con el tratamiento
            cita = self.db_session.query(Cita).filter_by(id_tratamiento=id_tratamiento).first()
            if not cita:
                logging.error(f"No se encontró una cita para el tratamiento con ID {id_tratamiento}.")
                return {"error": "Cita no encontrada para el tratamiento especificado"}
            
            # Obtener el cliente y la mascota
            cliente = self.db_session.query(Cliente).filter_by(id_cliente=cita.id_cliente).first()
            mascota = self.db_session.query(Mascota).filter_by(id_mascota=cita.id_mascota).first()
            if not cliente or not mascota:
                logging.error(f"Cliente o mascota no encontrados para la cita con ID {cita.id_cita}.")
                return {"error": "Cliente o mascota no encontrados"}
            
            # Retornar todos los datos necesarios
            return {
                "cliente": cliente,
                "mascota": mascota,
                "cita": cita,
                "tratamiento": tratamiento
            }

        except SQLAlchemyError as e:
            logging.critical(f"Error al acceder a la base de datos: {e}")
            return {"error": "Error de base de datos al obtener los datos de la factura"}

        except Exception as e:
            logging.critical(f"Error inesperado al obtener datos de factura: {e}")
            return {"error": "Ocurrió un error inesperado al obtener los datos de la factura"}
    
    def validar_tratamiento_completado(self, tratamiento: Tratamiento):
        """
        Valida si el tratamiento está marcado como completado.
        Devuelve True si el tratamiento está completado, de lo contrario devuelve False.
        """
        try:
            # Verifica si el atributo `estado` existe y tiene un valor
            if getattr(tratamiento, 'estado', None) is None:
                logging.error("El modelo Tratamiento no tiene el atributo 'estado' o está configurado en None.")
                return {"error": "El modelo Tratamiento no tiene el atributo 'estado'"}
            
            # Aquí se asume que el tratamiento tiene un campo 'estado' que indica si está completado.
            if tratamiento.estado == "Completado":
                logging.info(f"Tratamiento con ID {tratamiento.id_tratamiento} está completado.")
                return True
            logging.warning(f"Tratamiento con ID {tratamiento.id_tratamiento} no está completado.")
            return False

        except AttributeError as e:
            logging.error(f"El modelo Tratamiento no tiene el atributo 'estado': {e}")
            return {"error": "El modelo Tratamiento no tiene el atributo 'estado'"}

        except Exception as e:
            logging.critical(f"Error inesperado al validar el estado del tratamiento: {e}")
            return {"error": "Ocurrió un error inesperado al validar el estado del tratamiento"}
