import logging
import os
import json
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from clinica.services.gestion_clientes import GestionClientes
from clinica.models.tabla_cliente import Cliente as ClienteModel
from clinica.models.tabla_mascota import Mascota as MascotaModel

class GestionMascotas(GestionClientes):

    def exportar_mascotas_a_json(self, ruta_json=None):
        """Exporta las mascotas a un archivo JSON."""
        if ruta_json is None:
            # Establece la ruta por defecto usando el directorio actual de trabajo
            ruta_json = os.path.join(os.getcwd(), 'clinica/data/datos_mascotas.json')

        try:
            # Obtener todas las mascotas de la base de datos y convertir cada una en diccionario
            mascotas = self.db_session.query(MascotaModel).all()
            datos = [mascota.to_dict() for mascota in mascotas]  # Usando to_dict()

            # Guardar los datos en el archivo JSON
            with open(ruta_json, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=4)
            logging.info(f"Mascotas exportadas a {ruta_json} exitosamente.")
        except Exception as e:
            logging.error(f"Error al exportar mascotas a JSON: {e}")
            raise



    def registrar_mascota(self, id_cliente, mascota_data):
        """Registra una nueva mascota para un cliente existente."""
        try:
            # Verificar si el cliente existe
            cliente = self.db_session.query(ClienteModel).filter_by(id_cliente=id_cliente).first()

            if not cliente:
                logging.warning("Cliente no encontrado.")
                return "Cliente no encontrado."

            # Eliminar `id_cliente` de mascota_data si existe para evitar duplicación
            mascota_data.pop("id_cliente", None)

            # Crear y añadir la nueva mascota
            nueva_mascota = MascotaModel(**mascota_data, id_cliente=id_cliente)
            self.db_session.add(nueva_mascota)
            self.db_session.commit()
            self.db_session.refresh(nueva_mascota)

            logging.info(f"Mascota '{mascota_data['nombre_mascota']}' registrada para el cliente '{cliente.nombre_cliente}'.")

            # Retornar la instancia de la mascota registrada
            return nueva_mascota

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

    def modificar_mascota(self, id_mascota, nuevos_datos):
        """Modifica una mascota existente en la base de datos."""
        try:
            mascota = self.db_session.query(MascotaModel).filter_by(id_mascota=id_mascota).first()

            if mascota:
                for key, value in nuevos_datos.items():
                    setattr(mascota, key, value)
                self.db_session.commit()
                logging.info(f"Mascota con ID '{id_mascota}' modificada con éxito.")

                # Exportar a JSON después de la operación
                self.exportar_mascotas_a_json()

                return f"Mascota con ID '{id_mascota}' modificada con éxito."
            else:
                logging.warning(f"No se encontró la mascota con ID '{id_mascota}'.")
                return f"No se encontró la mascota con ID '{id_mascota}'."

        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al modificar la mascota: %s", sae)
            return f"Error al modificar la mascota: {sae}"

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al modificar la mascota: %s", e)
            return f"Ocurrió un error inesperado al modificar la mascota: {e}"

    def eliminar_mascota(self, id_mascota):
        """Elimina una mascota de la base de datos."""
        try:
            mascota = self.db_session.query(MascotaModel).filter_by(id_mascota=id_mascota).first()

            if mascota:
                self.db_session.delete(mascota)
                self.db_session.commit()
                logging.info(f"Mascota con ID '{id_mascota}' eliminada con éxito.")

                # Exportar a JSON después de la operación
                self.exportar_mascotas_a_json()

                return f"Mascota con ID '{id_mascota}' eliminada con éxito."
            else:
                logging.warning(f"No se encontró la mascota con ID '{id_mascota}'.")
                return f"No se encontró la mascota con ID '{id_mascota}'."

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

    def listar_mascotas_por_cliente(self, id_cliente):
        """Devuelve una lista de mascotas pertenecientes a un cliente específico."""
        try:
            mascotas = self.db_session.query(MascotaModel).filter_by(id_cliente=id_cliente).all()
            return mascotas
        except SQLAlchemyError as sae:
            logging.error("Error de SQLAlchemy al listar las mascotas por cliente: %s", sae)
            return []
        except Exception as e:
            logging.critical("Error inesperado al listar las mascotas por cliente: %s", e)
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

    def marcar_mascota_como_fallecido(self, id_cliente, nombre_mascota):
        """Marca una mascota como fallecida para un cliente específico."""
        try:
            mascota = self.db_session.query(MascotaModel).filter_by(id_cliente=id_cliente, nombre_mascota=nombre_mascota).first()

            if mascota:
                mascota.estado = "Fallecido"
                self.db_session.commit()
                logging.info(f"La mascota '{mascota.nombre_mascota}' ha sido marcada como fallecida.")

                # Exportar a JSON después de la operación (opcional)
                self.exportar_mascotas_a_json()

                return f"La mascota '{mascota.nombre_mascota}' ha sido marcada como fallecida."
            else:
                logging.warning(f"No se encontró la mascota '{nombre_mascota}' para el cliente con ID '{id_cliente}'.")
                return f"No se encontró la mascota '{nombre_mascota}' para el cliente con ID '{id_cliente}'."

        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al marcar la mascota como fallecida: %s", sae)
            return f"Error al marcar la mascota como fallecida: {sae}"

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al marcar la mascota como fallecida: %s", e)
            return f"Ocurrió un error inesperado al marcar la mascota como fallecida: {e}"