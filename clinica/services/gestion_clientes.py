import logging
import json
import os
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from clinica.models.tabla_cliente import Cliente as ClienteModel
from clinica.models.tabla_mascota import Mascota as MascotaModel

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GestionClientes:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def exportar_clientes_a_json(self, ruta_json=None):
        """Exporta los clientes a un archivo JSON."""
        if ruta_json is None:
            # Establece la ruta por defecto usando el directorio actual de trabajo
            ruta_json = os.path.join(os.getcwd(), 'clinica/data/tabla_clientes.json')

        # Verifica que el directorio exista y créalo si no existe
        directorio = os.path.dirname(ruta_json)
        if not os.path.exists(directorio):
            os.makedirs(directorio)
        
        try:
            clientes = self.db_session.query(ClienteModel).all()
            datos = [cliente.to_dict() for cliente in clientes]  # Asegúrate de que `to_dict()` esté implementado en `ClienteModel`
            
            with open(ruta_json, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=4)
            logging.info(f"Clientes exportados a {ruta_json} exitosamente.")
        except Exception as e:
            logging.error(f"Error al exportar clientes a JSON: {e}")


    def exportar_mascotas_a_json(self, ruta_json=None):
        """Exporta las mascotas a un archivo JSON."""
        if ruta_json is None:
            # Establece la ruta completa al archivo JSON
            ruta_json = os.path.abspath('clinica/data/tabla_mascotas.json')
        
        try:
            mascotas = self.db_session.query(MascotaModel).all()
            if not mascotas:
                logging.warning("No hay mascotas para exportar.")
            
            datos = [mascota.to_dict() for mascota in mascotas]  # Verifica que `to_dict()` funcione correctamente
            logging.debug(f"Datos a exportar: {datos}")  # Depuración
            
            with open(ruta_json, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=4)
            
            logging.info(f"Mascotas exportadas a {ruta_json} exitosamente.")
        except OSError as e:
            logging.error(f"Error de sistema al exportar mascotas a JSON: {e}")
        except Exception as e:
            logging.error(f"Error al exportar mascotas a JSON: {e}")



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

            logging.debug("Intentando registrar cliente con los siguientes datos: %s", cliente_data)
            nuevo_cliente = ClienteModel(**cliente_data)
            self.db_session.add(nuevo_cliente)
            self.db_session.commit()
            logging.info(f"Cliente '{cliente_data['nombre_cliente']}' registrado con éxito.")
            
            # Exportar a JSON después de la operación
            self.exportar_clientes_a_json()

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
        
    def modificar_cliente(self, cliente_id, nuevos_datos):
        """Modifica un cliente existente en la base de datos."""
        try:
            cliente = self.db_session.query(ClienteModel).filter_by(id_cliente=cliente_id).first()

            if cliente:
                for key, value in nuevos_datos.items():
                    setattr(cliente, key, value)
                self.db_session.commit()
                logging.info(f"Cliente con ID '{cliente_id}' modificado con éxito.")
                
                # Exportar a JSON después de la operación
                self.exportar_clientes_a_json()

                return f"Cliente con ID '{cliente_id}' modificado con éxito."
            else:
                logging.warning(f"No se encontró el cliente con ID '{cliente_id}'.")
                return f"No se encontró el cliente con ID '{cliente_id}'."

        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al modificar el cliente: %s", sae)
            return f"Error al modificar el cliente: {sae}"

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al modificar el cliente: %s", e)
            return f"Ocurrió un error inesperado al modificar el cliente: {e}"

    def eliminar_cliente(self, cliente_id):
        """Elimina un cliente de la base de datos."""
        try:
            cliente = self.db_session.query(ClienteModel).filter_by(id_cliente=cliente_id).first()

            if cliente:
                self.db_session.delete(cliente)
                self.db_session.commit()
                logging.info(f"Cliente con ID '{cliente_id}' eliminado con éxito.")
                
                # Exportar a JSON después de la operación
                self.exportar_clientes_a_json()

                return f"Cliente con ID '{cliente_id}' eliminado con éxito."
            else:
                logging.warning(f"No se encontró el cliente con ID '{cliente_id}'.")
                return f"No se encontró el cliente con ID '{cliente_id}'."

        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al eliminar el cliente: %s", sae)
            return f"Error al eliminar el cliente: {sae}"

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al eliminar el cliente: %s", e)
            return f"Ocurrió un error inesperado al eliminar el cliente: {e}"
        
    def buscar_cliente(self, dni):
        """Busca un cliente por su DNI."""
        try:
            cliente = self.db_session.query(ClienteModel).filter_by(dni=dni).first()
            return cliente
        except SQLAlchemyError as e:
            logging.error("Error al buscar cliente por DNI: %s", e)
            return None

    def buscar_cliente_por_nombre(self, nombre_cliente):
        """Busca clientes por nombre y muestra los nombres de las mascotas asociadas si hay múltiples coincidencias."""
        try:
            clientes = self.db_session.query(ClienteModel).filter(
                ClienteModel.nombre_cliente.ilike(f"%{nombre_cliente}%")
            ).all()

            if not clientes:
                logging.warning(f"No se encontró ningún cliente con el nombre '{nombre_cliente}'.")
                return None

            # Si hay un solo cliente, se devuelve directamente junto con sus mascotas
            if len(clientes) == 1:
                mascotas = self.db_session.query(MascotaModel).filter_by(id_cliente=clientes[0].id_cliente).all()
                nombres_mascotas = [mascota.nombre_mascota for mascota in mascotas]
                logging.info(f"Cliente encontrado: {clientes[0].nombre_cliente} (ID: {clientes[0].id_cliente}), Mascotas: {', '.join(nombres_mascotas) if nombres_mascotas else 'Ninguna'}")
                return {
                    "cliente": clientes[0],
                    "mascotas": nombres_mascotas
                }

            # Si hay múltiples clientes, se listan y se pide una selección
            logging.info(f"Se encontraron múltiples clientes con el nombre '{nombre_cliente}'.")
            for idx, cliente in enumerate(clientes, start=1):
                mascotas = self.db_session.query(MascotaModel).filter_by(id_cliente=cliente.id_cliente).all()
                nombres_mascotas = [mascota.nombre_mascota for mascota in mascotas]
                print(f"{idx}. {cliente.nombre_cliente} - ID: {cliente.id_cliente} - DNI: {cliente.dni} - Teléfono: {cliente.telefono} - Mascotas: {', '.join(nombres_mascotas) if nombres_mascotas else 'Ninguna'}")

            try:
                seleccion = int(input("Seleccione el número del cliente deseado (0 para cancelar): "))
                if seleccion == 0:
                    print("Operación cancelada.")
                    return None
                elif 1 <= seleccion <= len(clientes):
                    cliente_seleccionado = clientes[seleccion - 1]
                    mascotas = self.db_session.query(MascotaModel).filter_by(id_cliente=cliente_seleccionado.id_cliente).all()
                    nombres_mascotas = [mascota.nombre_mascota for mascota in mascotas]
                    logging.info(f"Cliente seleccionado: {cliente_seleccionado.nombre_cliente} (ID: {cliente_seleccionado.id_cliente})")
                    return {
                        "cliente": cliente_seleccionado,
                        "mascotas": nombres_mascotas
                    }
                else:
                    print("Selección no válida. Operación cancelada.")
                    return None

            except ValueError:
                print("Entrada no válida. Operación cancelada.")
                return None

        except SQLAlchemyError as sae:
            logging.error("Error de SQLAlchemy al buscar el cliente por nombre: %s", sae)
            return None

        except Exception as e:
            logging.critical("Error inesperado al buscar el cliente por nombre: %s", e)
            return None

        
    def listar_clientes(self):
        """Devuelve una lista de todos los clientes en la base de datos."""
        try:
            clientes = self.db_session.query(ClienteModel).all()
            logging.info("Listado de clientes obtenido con éxito.")
            return clientes

        except SQLAlchemyError as sae:
            logging.error("Error de SQLAlchemy al listar los clientes: %s", sae)
            return []

        except Exception as e:
            logging.critical("Error inesperado al listar los clientes: %s", e)
            return []



    def registrar_mascota(self, cliente_id, mascota_data):
        """Registra una nueva mascota para un cliente existente."""
        try:
            cliente = self.db_session.query(ClienteModel).filter_by(id_cliente=cliente_id).first()

            if cliente:
                nueva_mascota = MascotaModel(**mascota_data, id_cliente=cliente_id)
                self.db_session.add(nueva_mascota)
                self.db_session.commit()
                logging.info(f"Mascota '{mascota_data['nombre_mascota']}' registrada para el cliente '{cliente.nombre_cliente}'.")
                
                # Exportar a JSON después de la operación (opcional)
                self.exportar_mascotas_a_json()

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
        
    def modificar_mascota(self, mascota_id, nuevos_datos):
        """Modifica una mascota existente en la base de datos."""
        try:
            mascota = self.db_session.query(MascotaModel).filter_by(id_mascota=mascota_id).first()

            if mascota:
                for key, value in nuevos_datos.items():
                    setattr(mascota, key, value)
                self.db_session.commit()
                logging.info(f"Mascota con ID '{mascota_id}' modificada con éxito.")
                
                # Exportar a JSON después de la operación
                self.exportar_mascotas_a_json()

                return f"Mascota con ID '{mascota_id}' modificada con éxito."
            else:
                logging.warning(f"No se encontró la mascota con ID '{mascota_id}'.")
                return f"No se encontró la mascota con ID '{mascota_id}'."

        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al modificar la mascota: %s", sae)
            return f"Error al modificar la mascota: {sae}"

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al modificar la mascota: %s", e)
            return f"Ocurrió un error inesperado al modificar la mascota: {e}"

    def eliminar_mascota(self, mascota_id):
        """Elimina una mascota de la base de datos."""
        try:
            mascota = self.db_session.query(MascotaModel).filter_by(id_mascota=mascota_id).first()

            if mascota:
                self.db_session.delete(mascota)
                self.db_session.commit()
                logging.info(f"Mascota con ID '{mascota_id}' eliminada con éxito.")
                
                # Exportar a JSON después de la operación
                self.exportar_mascotas_a_json()

                return f"Mascota con ID '{mascota_id}' eliminada con éxito."
            else:
                logging.warning(f"No se encontró la mascota con ID '{mascota_id}'.")
                return f"No se encontró la mascota con ID '{mascota_id}'."

        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al eliminar la mascota: %s", sae)
            return f"Error al eliminar la mascota: {sae}"

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al eliminar la mascota: %s", e)
            return f"Ocurrió un error inesperado al eliminar la mascota: {e}"

    def listar_mascotas(self):
        """Devuelve una lista de todas las mascotas en la base de datos."""
        try:
            mascotas = self.db_session.query(MascotaModel).all()
            logging.info("Listado de mascotas obtenido con éxito.")
            return mascotas

        except SQLAlchemyError as sae:
            logging.error("Error de SQLAlchemy al listar las mascotas: %s", sae)
            return []

        except Exception as e:
            logging.critical("Error inesperado al listar las mascotas: %s", e)
            return []

    def buscar_mascota_por_nombre(self, nombre_mascota):
        """Busca mascotas por nombre y muestra el nombre del cliente asociado si hay múltiples coincidencias."""
        try:
            mascotas = self.db_session.query(MascotaModel).filter(
                MascotaModel.nombre_mascota.ilike(f"%{nombre_mascota}%")
            ).all()

            if not mascotas:
                logging.warning(f"No se encontró ninguna mascota con el nombre '{nombre_mascota}'.")
                return None

            # Si hay una sola mascota, se devuelve directamente con el nombre del cliente asociado
            if len(mascotas) == 1:
                cliente = self.db_session.query(ClienteModel).filter_by(id_cliente=mascotas[0].id_cliente).first()
                logging.info(f"Mascota encontrada: {mascotas[0].nombre_mascota} (ID: {mascotas[0].id_mascota}), Cliente: {cliente.nombre_cliente if cliente else 'Desconocido'}")
                return {
                    "mascota": mascotas[0],
                    "cliente": cliente.nombre_cliente if cliente else "Desconocido"
                }

            # Si hay múltiples mascotas, se listan y se pide una selección
            logging.info(f"Se encontraron múltiples mascotas con el nombre '{nombre_mascota}'.")
            for idx, mascota in enumerate(mascotas, start=1):
                cliente = self.db_session.query(ClienteModel).filter_by(id_cliente=mascota.id_cliente).first()
                print(f"{idx}. Mascota: {mascota.nombre_mascota} - ID: {mascota.id_mascota} - Estado: {mascota.estado} - Cliente: {cliente.nombre_cliente if cliente else 'Desconocido'}")

            try:
                seleccion = int(input("Seleccione el número de la mascota deseada (0 para cancelar): "))
                if seleccion == 0:
                    print("Operación cancelada.")
                    return None
                elif 1 <= seleccion <= len(mascotas):
                    mascota_seleccionada = mascotas[seleccion - 1]
                    cliente = self.db_session.query(ClienteModel).filter_by(id_cliente=mascota_seleccionada.id_cliente).first()
                    logging.info(f"Mascota seleccionada: {mascota_seleccionada.nombre_mascota} (ID: {mascota_seleccionada.id_mascota}), Cliente: {cliente.nombre_cliente if cliente else 'Desconocido'}")
                    return {
                        "mascota": mascota_seleccionada,
                        "cliente": cliente.nombre_cliente if cliente else "Desconocido"
                    }
                else:
                    print("Selección no válida. Operación cancelada.")
                    return None

            except ValueError:
                print("Entrada no válida. Operación cancelada.")
                return None

        except SQLAlchemyError as sae:
            logging.error("Error de SQLAlchemy al buscar la mascota por nombre: %s", sae)
            return None

        except Exception as e:
            logging.critical("Error inesperado al buscar la mascota por nombre: %s", e)
            return None



    def marcar_mascota_como_fallecido(self, cliente_id, nombre_mascota):
        """Marca una mascota como fallecida para un cliente específico."""
        try:
            mascota = self.db_session.query(MascotaModel).filter_by(id_cliente=cliente_id, nombre_mascota=nombre_mascota).first()

            if mascota:
                mascota.estado = "Fallecido"
                self.db_session.commit()
                logging.info(f"La mascota '{mascota.nombre_mascota}' ha sido marcada como fallecida.")
                
                # Exportar a JSON después de la operación (opcional)
                self.exportar_mascotas_a_json()

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
