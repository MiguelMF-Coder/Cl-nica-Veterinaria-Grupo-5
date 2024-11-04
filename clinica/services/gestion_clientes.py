# gestion_clientes.py

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from clinica.models.tabla_cliente import Cliente as ClienteModel
from clinica.models.tabla_mascota import Mascota as MascotaModel

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GestionClientes:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def registrar_cliente(self, cliente_data):
        """Registra un nuevo cliente en la base de datos."""
        try:
            cliente_existente = self.db_session.query(ClienteModel).filter(
                (ClienteModel.dni == cliente_data['dni']) |
                (ClienteModel.telefono == cliente_data['telefono'])
            ).first()

            if cliente_existente:
                logging.warning(f"El cliente con DNI '{cliente_data['dni']}' o Teléfono '{cliente_data['telefono']}' ya está registrado.")
                return f"El cliente con DNI '{cliente_data['dni']}' o Teléfono '{cliente_data['telefono']}' ya está registrado."

            nuevo_cliente = ClienteModel(**cliente_data)
            self.db_session.add(nuevo_cliente)
            self.db_session.commit()
            logging.info(f"Cliente '{cliente_data['nombre_cliente']}' registrado con éxito.")
            return f"Cliente '{cliente_data['nombre_cliente']}' registrado con éxito."

        except IntegrityError as ie:
            self.db_session.rollback()
            logging.error("Error de integridad al registrar el cliente: %s", ie)
            return "Error: No se pudo registrar el cliente debido a un problema de integridad."

        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al registrar el cliente: %s", sae)
            return f"Error: Ocurrió un problema con la base de datos: {sae}"

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al registrar el cliente: %s", e)
            return f"Ocurrió un error inesperado al registrar el cliente: {e}"

    def buscar_cliente(self, dni=None, telefono=None):
        """Busca un cliente por DNI o teléfono y devuelve el cliente encontrado."""
        try:
            cliente = self.db_session.query(ClienteModel).filter(
                (ClienteModel.dni == dni) | (ClienteModel.telefono == telefono)
            ).first()

            if cliente:
                logging.info(f"Cliente encontrado: {cliente.nombre_cliente}")
                return cliente
            else:
                logging.warning("Cliente no encontrado.")
                return None

        except SQLAlchemyError as sae:
            logging.error("Error de SQLAlchemy al buscar el cliente: %s", sae)
            return None

        except Exception as e:
            logging.critical("Error inesperado al buscar el cliente: %s", e)
            return None

    def registrar_mascota(self, cliente_id, mascota_data):
        """Registra una nueva mascota para un cliente existente."""
        try:
            cliente = self.db_session.query(ClienteModel).filter_by(id_cliente=cliente_id).first()

            if cliente:
                nueva_mascota = MascotaModel(**mascota_data, id_cliente=cliente_id)
                self.db_session.add(nueva_mascota)
                self.db_session.commit()
                logging.info(f"Mascota '{mascota_data['nombre_mascota']}' registrada para el cliente '{cliente.nombre_cliente}'.")
                return f"Mascota '{mascota_data['nombre_mascota']}' registrada para el cliente '{cliente.nombre_cliente}'."
            else:
                logging.warning("Cliente no encontrado.")
                return "Cliente no encontrado."

        except IntegrityError as ie:
            self.db_session.rollback()
            logging.error("Error de integridad al registrar la mascota: %s", ie)
            return "Error: No se pudo registrar la mascota debido a un problema de integridad."

        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al registrar la mascota: %s", sae)
            return f"Error: Ocurrió un problema con la base de datos: {sae}"

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al registrar la mascota: %s", e)
            return f"Ocurrió un error inesperado al registrar la mascota: {e}"

    def marcar_mascota_como_fallecido(self, cliente_id, nombre_mascota):
        """Marca una mascota como fallecida para un cliente específico."""
        try:
            mascota = self.db_session.query(MascotaModel).filter_by(id_cliente=cliente_id, nombre_mascota=nombre_mascota).first()

            if mascota:
                mascota.estado = "Fallecido"
                self.db_session.commit()
                logging.info(f"La mascota '{mascota.nombre_mascota}' ha sido marcada como fallecida.")
                return f"La mascota '{mascota.nombre_mascota}' ha sido marcada como fallecida."
            else:
                logging.warning(f"No se encontró la mascota '{nombre_mascota}' para el cliente con ID '{cliente_id}'.")
                return f"No se encontró la mascota '{nombre_mascota}' para el cliente con ID '{cliente_id}'."

        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al marcar la mascota como fallecida: %s", sae)
            return f"Error al marcar la mascota como fallecida: {sae}"

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al marcar la mascota como fallecida: %s", e)
            return f"Ocurrió un error inesperado al marcar la mascota como fallecida: {e}"
