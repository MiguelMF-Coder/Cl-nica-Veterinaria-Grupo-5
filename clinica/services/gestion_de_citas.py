# gestion_de_citas.py

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from clinica.models.tabla_citas import Cita
from clinica.models.tabla_tratamiento import Tratamiento  # Asegúrate de que la importación sea correcta

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GestionCitas:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def registrar_cita(self, cita_data):
        """Registra una nueva cita en la base de datos."""
        try:
            # Verificar si la cita ya existe en la base de datos
            cita_existente = self.db_session.query(Cita).filter_by(
                fecha=cita_data['fecha'],
                descripcion=cita_data['descripcion'],
                id_mascota=cita_data['id_mascota'],
                id_cliente=cita_data['id_cliente']
            ).first()

            if cita_existente:
                raise ValueError("Ya existe una cita para este animal, dueño y horario.")

            nueva_cita = Cita(**cita_data)
            self.db_session.add(nueva_cita)
            self.db_session.commit()
            logging.info(f"Cita registrada con éxito para el cliente ID {cita_data['id_cliente']}.")
            return f"Cita registrada con éxito para el cliente ID {cita_data['id_cliente']}."
        
        except IntegrityError as ie:
            self.db_session.rollback()
            logging.error("Error de integridad al registrar la cita: %s", ie)
            return "Error: No se pudo registrar la cita debido a un problema de integridad."
        
        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al registrar la cita: %s", sae)
            return f"Error: Ocurrió un problema con la base de datos: {sae}"
    
    # Eliminar la captura genérica de excepciones para que ValueError se propague


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

    def modificar_cita(self, cita_id, nuevos_datos):
        """Modifica el tratamiento o la fecha de una cita existente."""
        try:
            cita = self.db_session.query(Cita).filter_by(id_cita=cita_id).first()
            if cita:
                # Actualizar los atributos de la cita con los nuevos datos
                for key, value in nuevos_datos.items():
                    if hasattr(cita, key):
                        setattr(cita, key, value)
                
                self.db_session.commit()
                logging.info(f"Cita con ID '{cita_id}' modificada con éxito.")
                return f"Cita con ID '{cita_id}' modificada con éxito."
            else:
                logging.warning(f"No se encontró la cita con ID '{cita_id}'.")
                return f"Error: No se encontró la cita con ID '{cita_id}'."
        
        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al modificar la cita: %s", sae)
            return f"Error al modificar la cita: {sae}"

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al modificar la cita: %s", e)
            return f"Ocurrió un error inesperado al modificar la cita: {e}"

    def cancelar_cita(self, cita_id):
        """Cancela una cita eliminándola de la base de datos."""
        try:
            cita = self.db_session.query(Cita).filter_by(id_cita=cita_id).first()
            if cita:
                self.db_session.delete(cita)
                self.db_session.commit()
                logging.info(f"Cita con ID '{cita_id}' cancelada con éxito.")
                return f"Cita con ID '{cita_id}' cancelada con éxito."
            else:
                logging.warning(f"No se encontró la cita con ID '{cita_id}'.")
                return f"Error: No se encontró la cita con ID '{cita_id}'."
        
        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al cancelar la cita: %s", sae)
            return f"Error al cancelar la cita: {sae}"

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al cancelar la cita: %s", e)
            return f"Ocurrió un error inesperado al cancelar la cita: {e}"

    def finalizar_cita(self, cita_id, tratamientos_realizados, metodo_pago):
        """Finaliza la cita y establece el método de pago en la factura."""
        try:
            cita = self.db_session.query(Cita).filter_by(id_cita=cita_id).first()
            if cita:
                cita.finalizar_cita(tratamientos_realizados)
                cita.factura.establecer_metodo_pago(metodo_pago)
                logging.info(f"Cita con ID '{cita_id}' finalizada y método de pago '{metodo_pago}' registrado.")
                return "Método de pago registrado y cita finalizada."
            else:
                logging.warning(f"No se encontró la cita con ID '{cita_id}'.")
                return f"Error: No se encontró la cita con ID '{cita_id}'."

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
