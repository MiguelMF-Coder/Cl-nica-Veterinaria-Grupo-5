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
            
            # Control adicional: verificar si hay citas registradas
            if not citas:
                mensaje = "No hay citas registradas para exportar."
                logging.warning(mensaje)
                return {"warning": mensaje}

            # Convertir las citas a diccionarios
            datos = [cita.to_dict() for cita in citas]  # Asegúrate de que `to_dict()` esté implementado en `Cita`
            
            # Exportar a JSON
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

            
    def registrar_cita(self, cita_data, validar_duplicados=True):
        """Registra una nueva cita en la base de datos."""
        try:
            # Validar campos obligatorios
            campos_requeridos = ['fecha', 'descripcion', 'id_mascota', 'id_cliente', 'id_tratamiento', 'estado']
            for campo in campos_requeridos:
                if campo not in cita_data:
                    raise ValueError(f"El campo '{campo}' es obligatorio para registrar una cita.")

            # Validar estado
            estados_permitidos = {"Pendiente", "Finalizada", "Cancelada"}
            if cita_data['estado'] not in estados_permitidos:
                raise ValueError(f"Estado '{cita_data['estado']}' no es válido. Estados permitidos: {', '.join(estados_permitidos)}.")

            # Verificar duplicados solo si está habilitado
            if validar_duplicados:
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
            return nueva_cita

        except IntegrityError as ie:
            self.db_session.rollback()
            logging.error("Error de integridad al registrar la cita: %s", ie)
            raise ValueError("Error: No se pudo registrar la cita debido a un problema de integridad.")

        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al registrar la cita: %s", sae)
            raise RuntimeError(f"Error: Ocurrió un problema con la base de datos: {sae}")

    def ver_todas_las_citas(self, estado=None):
        print("Entrando en ver_todas_las_citas...")  # DEBUG
        try:
            query = self.db_session.query(Cita)
            print("Query inicial:", query)  # DEBUG

            if estado:
                query = query.filter(Cita.estado == estado)
                print("Filtro aplicado:", query)  # DEBUG

            total_citas = query.count()
            print("Total de citas filtradas:", total_citas)  # DEBUG

            citas = query.all()
            print("Citas obtenidas:", citas)  # DEBUG

            return {
                "total": total_citas,
                "citas": [cita.to_dict() for cita in citas],
            }
        except Exception as e:
            print("Error en ver_todas_las_citas:", str(e))  # DEBUG
            return {"error": str(e)}


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
        """Modifica una cita existente."""
        try:
            cita = self.db_session.query(Cita).filter_by(id_cita=id_cita).first()
            if cita:
                # Actualizar los atributos de la cita con los nuevos datos
                for key, value in nuevos_datos.items():
                    if hasattr(cita, key):
                        setattr(cita, key, value)
                
                self.db_session.commit()
                logging.info(f"Cita con ID '{id_cita}' modificada con éxito.")
                return cita
            else:
                logging.warning(f"No se encontró la cita con ID '{id_cita}'.")
                return None
        
        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al modificar la cita: %s", sae)
            raise RuntimeError(f"Error al modificar la cita: {sae}")

    def cancelar_cita(self, id_cita):
        """Cancela una cita eliminándola de la base de datos."""
        try:
            cita = self.db_session.query(Cita).filter_by(id_cita=id_cita).first()
            if cita:
                cita.estado = "Cancelada"
                self.db_session.commit()
                logging.info(f"Cita con ID '{id_cita}' cancelada con éxito.")
                return cita
            else:
                logging.warning(f"No se encontró la cita con ID '{id_cita}'.")
                return None
        
        except SQLAlchemyError as sae:
            self.db_session.rollback()
            logging.error("Error de SQLAlchemy al cancelar la cita: %s", sae)
            raise RuntimeError(f"Error al cancelar la cita: {sae}")

    def finalizar_cita(self, id_cita, metodo_pago):
        """Finaliza la cita y establece el método de pago."""
        try:
            # Validar el método de pago
            if metodo_pago not in {"Efectivo", "Tarjeta", "Bizum", "Transferencia"}:
                raise ValueError(f"Método de pago '{metodo_pago}' no es válido. Métodos aceptados: Efectivo, Tarjeta, Bizum, Transferencia.")
            
            # Buscar la cita en la base de datos
            cita = self.db_session.query(Cita).filter_by(id_cita=id_cita).first()
            if not cita:
                logging.warning(f"No se encontró la cita con ID '{id_cita}'.")
                return None

            # Finalizar la cita
            cita.metodo_pago = metodo_pago  # Registrar el método de pago
            cita.estado = "Finalizada"  # Cambiar el estado de la cita

            self.db_session.commit()
            logging.info(f"Cita con ID '{id_cita}' finalizada correctamente con método de pago '{metodo_pago}'.")
            return cita

        except ValueError as ve:
            logging.error("Error en la validación: %s", ve)
            raise ve

        except SQLAlchemyError as sae:
            logging.error("Error de base de datos al finalizar la cita: %s", sae)
            self.db_session.rollback()
            raise RuntimeError(f"Error al finalizar la cita: {sae}")

    def buscar_cita_por_id(self, id_cita: int):
        """Busca una cita por su ID."""
        try:
            cita = self.db_session.query(Cita).filter_by(id_cita=id_cita).first()
            return cita
        except Exception as e:
            logging.error(f"Error al buscar cita por ID: {e}")
            return None
