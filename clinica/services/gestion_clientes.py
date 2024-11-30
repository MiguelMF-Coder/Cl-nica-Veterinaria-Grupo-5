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
        if ruta_json is None:
            ruta_json = os.path.join(os.getcwd(), 'clinica/data/tabla_clientes.json')

        # Verifica que el directorio exista y créalo si no existe
        directorio = os.path.dirname(ruta_json)
        if not os.path.exists(directorio):
            os.makedirs(directorio)
        
        try:
            clientes = self.db_session.query(ClienteModel).all()
            datos = [cliente.to_dict() for cliente in clientes]  # Asegúrate de que `to_dict()` esté implementado en `ClienteModel`
            
            print("Clientes exportados:", datos)  # Depuración: Verifica los datos antes de escribir

            with open(ruta_json, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=4)
            logging.info(f"Clientes exportados a {ruta_json} exitosamente.")
        except Exception as e:
            logging.error(f"Error al exportar clientes a JSON: {e}")


    def registrar_cliente(self, cliente_data):
        """
        Registra un nuevo cliente en la base de datos con validaciones mejoradas.
        
        Args:
            cliente_data (dict): Diccionario con los datos del cliente a registrar
            
        Returns:
            ClienteModel o dict: Retorna el modelo del cliente si el registro es exitoso,
                            o un diccionario con mensaje de error si falla
        """
        try:
            # Aseguramos que el teléfono sea string antes de cualquier operación
            # Esto evita problemas de tipo más adelante
            if 'telefono' in cliente_data:
                cliente_data['telefono'] = str(cliente_data['telefono'])

            # Validaciones preliminares
            if not self._validar_formato_dni(cliente_data.get('dni', '')):
                return {"error": "El formato del DNI no es válido"}
                
            if not self._validar_formato_telefono(cliente_data['telefono']):
                return {"error": "El formato del teléfono no es válido"}

            # Verificar cliente duplicado con el teléfono ya convertido a string
            cliente_existente = self.db_session.query(ClienteModel).filter(
                (ClienteModel.dni == cliente_data['dni']) |
                (ClienteModel.telefono == cliente_data['telefono'])
            ).first()
            
            if cliente_existente:
                mensaje_error = (
                    f"Cliente con DNI '{cliente_data['dni']}' o "
                    f"Teléfono '{cliente_data['telefono']}' ya registrado."
                )
                logging.warning(mensaje_error)
                return {"error": mensaje_error}

            # Crear y guardar el nuevo cliente
            nuevo_cliente = ClienteModel(**cliente_data)
            self.db_session.add(nuevo_cliente)
            self.db_session.commit()
            
            # Refrescar para asegurar que tenemos todos los datos actualizados
            self.db_session.refresh(nuevo_cliente)
            
            # Log de éxito
            logging.info(
                f"Cliente registrado exitosamente - DNI: {cliente_data['dni']}, "
                f"Teléfono: {cliente_data['telefono']}"
            )
            
            return nuevo_cliente
        
        except IntegrityError as ie:
            self.db_session.rollback()
            mensaje_error = "Error: No se pudo registrar el cliente debido a un problema de integridad."
            logging.error(f"{mensaje_error} Detalle: {str(ie)}")
            return {"error": mensaje_error}
            
        except SQLAlchemyError as sae:
            self.db_session.rollback()
            mensaje_error = f"Error: Ocurrió un problema con la base de datos: {str(sae)}"
            logging.error(mensaje_error)
            return {"error": mensaje_error}
            
        except Exception as e:
            self.db_session.rollback()
            mensaje_error = f"Ocurrió un error inesperado al registrar el cliente: {str(e)}"
            logging.critical(mensaje_error)
            return {"error": mensaje_error}

    def _validar_formato_dni(self, dni: str) -> bool:
        """
        Valida que el formato del DNI sea correcto.
        
        Args:
            dni (str): DNI a validar
            
        Returns:
            bool: True si el formato es válido, False en caso contrario
        """
        if not dni:
            return False
        
        # El DNI debe tener 8 números seguidos de una letra
        if len(dni) != 9:
            return False
            
        numeros = dni[:-1]
        letra = dni[-1]
        
        return numeros.isdigit() and letra.isalpha()

    def _validar_formato_telefono(self, telefono: str) -> bool:
        """
        Valida que el formato del teléfono sea correcto.
        
        Args:
            telefono (str): Teléfono a validar
            
        Returns:
            bool: True si el formato es válido, False en caso contrario
        """
        if not telefono:
            return False
            
        # Convertir a string si no lo es
        telefono = str(telefono)
        
        # Debe tener 9 dígitos y empezar por 6, 7 o 9
        return (
            len(telefono) == 9 and
            telefono.isdigit() and
            telefono[0] in ('6', '7', '9')
        )


        
    def modificar_cliente(self, id_cliente, nuevos_datos):
        """Modifica un cliente existente en la base de datos."""
        try:
            cliente = self.db_session.query(ClienteModel).filter_by(id_cliente=id_cliente).first()

            if cliente:
                for key, value in nuevos_datos.items():
                    setattr(cliente, key, value)
                self.db_session.commit()
                logging.info(f"Cliente con ID '{id_cliente}' modificado con éxito.")
                
                # Exportar a JSON después de la operación
                self.exportar_clientes_a_json()

                return f"Cliente con ID '{id_cliente}' modificado con éxito."
            else:
                logging.warning(f"No se encontró el cliente con ID '{id_cliente}'.")
                return f"No se encontró el cliente con ID '{id_cliente}'."

        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al modificar el cliente: %s", sae)
            return f"Error al modificar el cliente: {sae}"

        except Exception as e:
            self.db_session.rollback()
            logging.critical("Error inesperado al modificar el cliente: %s", e)
            return f"Ocurrió un error inesperado al modificar el cliente: {e}"

    def eliminar_cliente(self, id_cliente):
        """Elimina un cliente de la base de datos."""
        try:
            cliente = self.db_session.query(ClienteModel).filter_by(id_cliente=id_cliente).first()

            if cliente:
                self.db_session.delete(cliente)
                self.db_session.commit()
                logging.info(f"Cliente con ID '{id_cliente}' eliminado con éxito.")
                
                # Exportar a JSON después de la operación
                self.exportar_clientes_a_json()

                return f"Cliente con ID '{id_cliente}' eliminado con éxito."
            else:
                logging.warning(f"No se encontró el cliente con ID '{id_cliente}'.")
                return f"No se encontró el cliente con ID '{id_cliente}'."

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