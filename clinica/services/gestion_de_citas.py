# gestion_de_citas.py

import logging
import os
import json
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from clinica.models.tabla_citas import Cita

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GestionCitas:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def exportar_citas_a_json(self, ruta_json=None):
            """Exporta las citas a un archivo JSON."""
            if ruta_json is None:
                ruta_json = os.path.join(os.getcwd(), 'clinica/data/tabla_citas.json')

            # Verifica que el directorio exista y créalo si no existe
            directorio = os.path.dirname(ruta_json)
            if not os.path.exists(directorio):
                os.makedirs(directorio)
            
            try:
                citas = self.db_session.query(Cita).all()
                datos = [cita.to_dict() for cita in citas]  # Asegúrate de que `to_dict()` esté implementado en `Cita`
                
                with open(ruta_json, 'w', encoding='utf-8') as archivo:
                    json.dump(datos, archivo, ensure_ascii=False, indent=4)
                logging.info(f"Citas exportadas a {ruta_json} exitosamente.")
                return f"Citas exportadas a {ruta_json} exitosamente."
            except SQLAlchemyError as e:
                logging.error(f"Error al exportar citas a JSON: {e}")
                return {"error": f"Error al exportar citas a JSON: {e}"}
            except Exception as e:
                logging.error(f"Error inesperado al exportar citas a JSON: {e}")
                return {"error": f"Error inesperado al exportar citas a JSON: {e}"}
            
    def registrar_cita(self, cita_data):
        """Registra una nueva cita en la base de datos."""
        try:
            # Verificar si la cita ya existe en la base de datos
            cita_existente = self.db_session.query(Cita).filter_by(
                fecha=cita_data['fecha'],
                descripcion=cita_data['descripcion'],
                id_mascota=cita_data['id_mascota'],
                id_cliente=cita_data['id_cliente'],
                id_tratamiento=cita_data['id_tratamiento']

            ).first()

            if cita_existente:
                raise ValueError("Ya existe una cita para este animal, dueño y horario.")

            # Crear y añadir la nueva cita a la base de datos
            nueva_cita = Cita(**cita_data)
            self.db_session.add(nueva_cita)
            self.db_session.commit()
            self.db_session.refresh(nueva_cita)
            
            logging.info(f"Cita registrada con éxito para el cliente ID {cita_data['id_cliente']}.")
            
            # Devolver el objeto `Cita` registrado
            return nueva_cita

        except IntegrityError as ie:
            self.db_session.rollback()
            logging.error("Error de integridad al registrar la cita: %s", ie)
            raise ValueError("Error: No se pudo registrar la cita debido a un problema de integridad.")

        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al registrar la cita: %s", sae)
            raise RuntimeError(f"Error: Ocurrió un problema con la base de datos: {sae}")


    def ver_todas_las_citas(self):
        """Muestra todas las citas registradas en la base de datos."""
        try:
            citas = self.db_session.query(Cita).all()
            if not citas:
                return "No hay citas registradas."
            else:
                resultado = "\n--- Todas las Citas ---\n" + "\n".join(str(cita) for cita in citas)
                return resultado
        
        except SQLAlchemyError as sae:
            logging.error("Error de SQLAlchemy al mostrar las citas: %s", sae)
            return f"Error al mostrar las citas: {sae}"
        
        except Exception as e:
            logging.critical("Error inesperado al mostrar las citas: %s", e)
            return f"Ocurrió un error inesperado al mostrar las citas: {e}"

    def buscar_cita(self, id_mascota, id_cliente):
        """Busca una cita por el ID de la mascota y el cliente."""
        try:
            cita = self.db_session.query(Cita).filter_by(
                id_mascota=id_mascota,
                id_cliente=id_cliente
            ).first()
            return cita

        except SQLAlchemyError as sae:
            logging.error("Error de SQLAlchemy al buscar la cita: %s", sae)
            return None
        
        except Exception as e:
            logging.critical("Error inesperado al buscar la cita: %s", e)
            return None

    def modificar_cita(self, id_cita, nuevos_datos):
        """Modifica el tratamiento o la fecha de una cita existente."""
        try:
            cita = self.db_session.query(Cita).filter_by(id_cita=id_cita).first()
            if cita:
                # Actualizar los atributos de la cita con los nuevos datos
                for key, value in nuevos_datos.items():
                    if hasattr(cita, key):
                        setattr(cita, key, value)
                
                self.db_session.commit()
                logging.info(f"Cita con ID '{id_cita}' modificada con éxito.")
                return f"Cita con ID '{id_cita}' modificada con éxito."
            else:
                logging.warning(f"No se encontró la cita con ID '{id_cita}'.")
                return f"Error: No se encontró la cita con ID '{id_cita}'."
        
        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al modificar la cita: %s", sae)
            return f"Error al modificar la cita: {sae}"

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al modificar la cita: %s", e)
            return f"Ocurrió un error inesperado al modificar la cita: {e}"

    def cancelar_cita(self, id_cita):
        """Cancela una cita eliminándola de la base de datos."""
        try:
            cita = self.db_session.query(Cita).filter_by(id_cita=id_cita).first()
            if cita:
                self.db_session.delete(cita)
                self.db_session.commit()
                logging.info(f"Cita con ID '{id_cita}' cancelada con éxito.")
                return f"Cita con ID '{id_cita}' cancelada con éxito."
            else:
                logging.warning(f"No se encontró la cita con ID '{id_cita}'.")
                return f"Error: No se encontró la cita con ID '{id_cita}'."
        
        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al cancelar la cita: %s", sae)
            return f"Error al cancelar la cita: {sae}"

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al cancelar la cita: %s", e)
            return f"Ocurrió un error inesperado al cancelar la cita: {e}"

    def finalizar_cita(self, id_cita, tratamientos_realizados, metodo_pago):
        """Finaliza la cita y establece el método de pago en la factura."""
        try:
            cita = self.db_session.query(Cita).filter_by(id_cita=id_cita).first()
            if cita:
                cita.finalizar_cita(tratamientos_realizados)
                cita.factura.establecer_metodo_pago(metodo_pago)
                logging.info(f"Cita con ID '{id_cita}' finalizada y método de pago '{metodo_pago}' registrado.")
                return "Método de pago registrado y cita finalizada."
            else:
                logging.warning(f"No se encontró la cita con ID '{id_cita}'.")
                return f"Error: No se encontró la cita con ID '{id_cita}'."

        except ValueError as ve:
            logging.error("Error al establecer el método de pago: %s", ve)
            self.db_session.rollback()
            return f"Error: {ve}"

        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al finalizar la cita: %s", sae)
            return f"Error al finalizar la cita: {sae}"

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al finalizar la cita: %s", e)
            return f"Ocurrió un error inesperado al finalizar la cita: {e}"
