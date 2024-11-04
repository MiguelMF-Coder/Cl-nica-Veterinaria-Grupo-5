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
                nombre_animal=cita_data['nombre_animal'],
                nombre_dueno=cita_data['nombre_dueno'],
                fecha_hora=cita_data['fecha_hora']
            ).first()

            if cita_existente:
                raise ValueError("Ya existe una cita para este animal, dueño y horario.")

            nueva_cita = Cita(**cita_data)
            self.db_session.add(nueva_cita)
            self.db_session.commit()
            logging.info(f"Cita registrada para {cita_data['nombre_animal']} con {cita_data['nombre_dueno']}.")
            print(f"Cita registrada para {cita_data['nombre_animal']} con {cita_data['nombre_dueno']}.")
        
        except IntegrityError as ie:
            self.db_session.rollback()
            logging.error("Error de integridad al registrar la cita: %s", ie)
            print("Error: No se pudo registrar la cita debido a un problema de integridad.")
        
        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al registrar la cita: %s", sae)
            print(f"Error: Ocurrió un problema con la base de datos: {sae}")
        
        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al registrar la cita: %s", e)
            print(f"Ocurrió un error inesperado al registrar la cita: {e}")

    def ver_todas_las_citas(self):
        """Muestra todas las citas registradas en la base de datos."""
        try:
            citas = self.db_session.query(Cita).all()
            if not citas:
                print("No hay citas registradas.")
            else:
                print("\n--- Todas las Citas ---")
                for cita in citas:
                    print(cita)
        
        except SQLAlchemyError as sae:
            logging.error("Error de SQLAlchemy al mostrar las citas: %s", sae)
            print(f"Error al mostrar las citas: {sae}")
        
        except Exception as e:
            logging.critical("Error inesperado al mostrar las citas: %s", e)
            print(f"Ocurrió un error inesperado al mostrar las citas: {e}")

    def buscar_cita(self, nombre_animal, nombre_dueno):
        """Busca una cita por el nombre del animal y el dueño."""
        try:
            cita = self.db_session.query(Cita).filter_by(
                nombre_animal=nombre_animal,
                nombre_dueno=nombre_dueno
            ).first()
            return cita

        except SQLAlchemyError as sae:
            logging.error("Error de SQLAlchemy al buscar la cita: %s", sae)
            print(f"Error al buscar la cita: {sae}")
            return None
        
        except Exception as e:
            logging.critical("Error inesperado al buscar la cita: %s", e)
            print(f"Ocurrió un error inesperado al buscar la cita: {e}")
            return None

    def modificar_cita(self, cita_id, nuevos_datos):
        """Modifica el tratamiento o la fecha de una cita existente."""
        try:
            cita = self.db_session.query(Cita).filter_by(id=cita_id).first()
            if cita:
                # Actualizar los atributos de la cita con los nuevos datos
                for key, value in nuevos_datos.items():
                    if hasattr(cita, key):
                        setattr(cita, key, value)
                
                self.db_session.commit()
                logging.info(f"Cita con ID '{cita_id}' modificada con éxito.")
                print(f"Cita con ID '{cita_id}' modificada con éxito.")
            else:
                logging.warning(f"No se encontró la cita con ID '{cita_id}'.")
                print(f"Error: No se encontró la cita con ID '{cita_id}'.")
        
        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al modificar la cita: %s", sae)
            print(f"Error al modificar la cita: {sae}")

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al modificar la cita: %s", e)
            print(f"Ocurrió un error inesperado al modificar la cita: {e}")

    def cancelar_cita(self, cita_id):
        """Cancela una cita eliminándola de la base de datos."""
        try:
            cita = self.db_session.query(Cita).filter_by(id=cita_id).first()
            if cita:
                self.db_session.delete(cita)
                self.db_session.commit()
                logging.info(f"Cita con ID '{cita_id}' cancelada con éxito.")
                print(f"Cita con ID '{cita_id}' cancelada con éxito.")
            else:
                logging.warning(f"No se encontró la cita con ID '{cita_id}'.")
                print(f"Error: No se encontró la cita con ID '{cita_id}'.")
        
        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al cancelar la cita: %s", sae)
            print(f"Error al cancelar la cita: {sae}")

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al cancelar la cita: %s", e)
            print(f"Ocurrió un error inesperado al cancelar la cita: {e}")

    def finalizar_cita(self, cita_id, tratamientos_realizados, metodo_pago):
        """Finaliza la cita y establece el método de pago en la factura."""
        try:
            cita = self.db_session.query(Cita).filter_by(id=cita_id).first()
            if cita:
                cita.finalizar_cita(tratamientos_realizados)
                cita.factura.establecer_metodo_pago(metodo_pago)
                logging.info(f"Cita con ID '{cita_id}' finalizada y método de pago '{metodo_pago}' registrado.")
                print("Método de pago registrado y cita finalizada.")
                print(cita.factura)
                self.db_session.commit()
            else:
                logging.warning(f"No se encontró la cita con ID '{cita_id}'.")
                print(f"Error: No se encontró la cita con ID '{cita_id}'.")

        except ValueError as ve:
            logging.error("Error al establecer el método de pago: %s", ve)
            print(f"Error: {ve}")
            self.db_session.rollback()

        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al finalizar la cita: %s", sae)
            print(f"Error al finalizar la cita: {sae}")

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al finalizar la cita: %s", e)
            print(f"Ocurrió un error inesperado al finalizar la cita: {e}")
