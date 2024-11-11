import sys
import os
import tempfile
import unittest
import unittest.mock
import json
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from clinica.dbconfig import Base
from clinica.models.tabla_cliente import Cliente as ClienteModel
from clinica.models.tabla_mascota import Mascota as MascotaModel
from clinica.services.gestion_clientes import GestionClientes
from clinica.services.gestion_mascotas import GestionMascotas

class TestGestionMascotas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configuración de la base de datos en memoria para pruebas
        cls.engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(cls.engine)  # Crea todas las tablas necesarias en la base de datos en memoria
        cls.Session = sessionmaker(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        # Eliminar las tablas después de todas las pruebas
        Base.metadata.drop_all(bind=cls.engine)

    def setUp(self):
        # Crear una nueva sesión para cada prueba
        self.session = self.Session()
        self.gestion_clientes = GestionClientes(self.session)
        self.gestion_mascotas = GestionMascotas(self.session)

        max_attempts = 100  # Límite de intentos para evitar ciclos infinitos

        # Generar un DNI único
        for _ in range(max_attempts):
            self.dni_unico = f'12345678{random.randint(0, 9)}'
            if not self.session.query(ClienteModel).filter_by(dni=self.dni_unico).first():
                break
        else:
            raise Exception("No se pudo generar un DNI único después de múltiples intentos.")

        # Generar un teléfono único
        for _ in range(max_attempts):
            self.telefono_unico = random.randint(600000000, 699999999)
            if not self.session.query(ClienteModel).filter_by(telefono=self.telefono_unico).first():
                break
        else:
            raise Exception("No se pudo generar un teléfono único después de múltiples intentos.")

    def tearDown(self):
        try:
            self.session.query(MascotaModel).delete()
            self.session.query(ClienteModel).delete()
            self.session.commit()
        except Exception as e:
            print(f"Error al limpiar la base de datos: {e}")
            self.session.rollback()
        finally:
            self.session.close()
            
    def test_exportar_mascotas_a_json_exitoso(self):
        # Datos de prueba para cliente y mascota
        cliente_data = {
            'nombre_cliente': 'Carlos Pérez',
            'edad': 45,
            'dni': self.dni_unico,
            'direccion': 'Calle Norte 101',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        cliente = self.gestion_clientes.buscar_cliente(dni=self.dni_unico)

        mascota_data = {
            'nombre_mascota': 'Luna',
            'raza': 'Labrador',
            'edad': 3,
            'afeccion': 'Ninguna',
            'estado': 'Vivo'
        }
        resultado_registro = self.gestion_mascotas.registrar_mascota(cliente.id_cliente, mascota_data)
        self.assertIsInstance(resultado_registro, MascotaModel)  # Verifica que se ha registrado correctamente como instancia de MascotaModel

        # Usar un archivo temporal para la exportación
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            temp_file_path = temp_file.name

        # Exportar mascotas a JSON
        self.gestion_mascotas.exportar_mascotas_a_json(temp_file_path)

        # Leer y verificar el archivo JSON
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            datos = json.load(f)

        # Asegurarse de que el archivo no esté vacío y contiene la mascota "Luna"
        self.assertGreater(len(datos), 0, "El archivo JSON está vacío")
        self.assertTrue(any(mascota['nombre_mascota'] == 'Luna' for mascota in datos))

        # Limpieza del archivo de prueba
        os.remove(temp_file_path)

    def test_exportar_mascotas_a_json_error(self):
        with unittest.mock.patch('builtins.open', side_effect=OSError("Error de acceso")):
            with self.assertLogs(level='ERROR') as log:
                try:
                    self.gestion_mascotas.exportar_mascotas_a_json('test_mascotas.json')
                except OSError:
                    pass  # Si el método vuelve a lanzar la excepción, podemos ignorarla aquí para validar el log

            self.assertIn("Error al exportar mascotas a JSON: Error de acceso", log.output[-1])


    def test_registrar_mascota_exitoso(self):
        # Datos de prueba del cliente
        cliente_data = {
            'nombre_cliente': 'Luis Gómez',
            'edad': 35,
            'dni': self.dni_unico,
            'direccion': 'Calle Nueva 101',
            'telefono': self.telefono_unico
        }

        # Registrar cliente y asegurar que se ha guardado correctamente
        self.gestion_clientes.registrar_cliente(cliente_data)
        cliente = self.gestion_clientes.buscar_cliente(self.dni_unico)
        self.assertIsNotNone(cliente, "El cliente no se encontró en la base de datos")

        # Datos de prueba de la mascota
        mascota_data = {
            'nombre_mascota': 'Max',
            'raza': 'Labrador',
            'edad': 3,
            'afeccion': 'Ninguna',
            'estado': 'Vivo'
        }

        # Registrar la mascota y verificar el resultado
        resultado = self.gestion_mascotas.registrar_mascota(cliente.id_cliente, mascota_data)
        self.assertIsInstance(resultado, MascotaModel, "La mascota no se registró correctamente como objeto.")



    def test_registrar_mascota_cliente_no_encontrado(self):
        mascota_data = {
            'nombre_mascota': 'Bella',
            'raza': 'Golden Retriever',
            'edad': 2,
            'afeccion': 'Ninguna',
            'estado': 'Vivo'
        }

        resultado = self.gestion_mascotas.registrar_mascota(9999, mascota_data)  # ID de cliente inexistente
        self.assertIn("Cliente no encontrado", resultado)

    def test_registrar_mascota_integrity_error(self):
        cliente_data = {
            'nombre_cliente': 'Marta López',
            'edad': 30,
            'dni': self.dni_unico,
            'direccion': 'Calle Prueba 123',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        cliente = self.gestion_clientes.buscar_cliente(dni=self.dni_unico)

        mascota_data = {
            'nombre_mascota': 'Lola',
            'raza': 'Beagle',
            'edad': 4,
            'afeccion': 'Alergias',
            'estado': 'Vivo'
        }

        with unittest.mock.patch.object(self.session, 'commit', side_effect=IntegrityError('mock', 'mock', 'mock')):
            resultado = self.gestion_mascotas.registrar_mascota(cliente.id_cliente, mascota_data)
            self.assertIn("Error: No se pudo registrar la mascota debido a un problema de integridad", resultado)

    def test_registrar_mascota_error_general(self):
        cliente_data = {
            'nombre_cliente': 'Jorge García',
            'edad': 40,
            'dni': self.dni_unico,
            'direccion': 'Calle Central 456',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        cliente = self.gestion_clientes.buscar_cliente(dni=self.dni_unico)

        mascota_data = {
            'nombre_mascota': 'Rocky',
            'raza': 'Boxer',
            'edad': 5,
            'afeccion': 'Artritis',
            'estado': 'Vivo'
        }

        with unittest.mock.patch.object(self.session, 'commit', side_effect=Exception("Error inesperado")):
            resultado = self.gestion_mascotas.registrar_mascota(cliente.id_cliente, mascota_data)
            self.assertIn("Ocurrió un error inesperado al registrar la mascota", resultado)

    def test_modificar_mascota_exitoso(self):
        cliente_data = {
            'nombre_cliente': 'Pedro López',
            'edad': 45,
            'dni': self.dni_unico,
            'direccion': 'Calle Mayor 222',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        cliente = self.gestion_clientes.buscar_cliente(dni=self.dni_unico)

        mascota_data = {
            'nombre_mascota': 'Rex',
            'raza': 'Bulldog',
            'edad': 5,
            'afeccion': 'Ninguna',
            'estado': 'Vivo'
        }
        self.gestion_mascotas.registrar_mascota(cliente.id_cliente, mascota_data)
        mascota = self.gestion_mascotas.listar_mascotas()[0]

        nuevos_datos = {
            'edad': 6,
            'estado': 'Fallecido'
        }
        resultado = self.gestion_mascotas.modificar_mascota(mascota.id_mascota, nuevos_datos)
        self.assertIn("modificada con éxito", resultado)

        mascota_modificada = self.gestion_mascotas.listar_mascotas()[0]
        self.assertEqual(mascota_modificada.edad, 6)
        self.assertEqual(mascota_modificada.estado, 'Fallecido')

    def test_modificar_mascota_no_encontrada(self):
        nuevos_datos = {
            'edad': 7,
            'estado': 'Fallecido'
        }
        resultado = self.gestion_mascotas.modificar_mascota(9999, nuevos_datos)  # ID de mascota inexistente
        self.assertIn("No se encontró la mascota con ID", resultado)

    def test_modificar_mascota_error(self):
        cliente_data = {
            'nombre_cliente': 'Sofía Pérez',
            'edad': 32,
            'dni': self.dni_unico,
            'direccion': 'Calle Sur 789',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        cliente = self.gestion_clientes.buscar_cliente(dni=self.dni_unico)

        mascota_data = {
            'nombre_mascota': 'Lucky',
            'raza': 'Beagle',
            'edad': 4,
            'afeccion': 'Ninguna',
            'estado': 'Vivo'
        }
        self.gestion_mascotas.registrar_mascota(cliente.id_cliente, mascota_data)
        mascota = self.gestion_mascotas.listar_mascotas()[0]

        nuevos_datos = {
            'edad': 8,
            'estado': 'En tratamiento'
        }

        with unittest.mock.patch.object(self.session, 'commit', side_effect=SQLAlchemyError("Error de SQLAlchemy")):
            resultado = self.gestion_mascotas.modificar_mascota(mascota.id_mascota, nuevos_datos)
            self.assertIn("Error al modificar la mascota", resultado)

    def test_eliminar_mascota_exitoso(self):
        cliente_data = {
            'nombre_cliente': 'Carlos Ruiz',
            'edad': 40,
            'dni': self.dni_unico,
            'direccion': 'Calle Principal 101',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        cliente = self.gestion_clientes.buscar_cliente(dni=self.dni_unico)

        mascota_data = {
            'nombre_mascota': 'Bella',
            'raza': 'Poodle',
            'edad': 2,
            'afeccion': 'Ninguna',
            'estado': 'Vivo'
        }
        self.gestion_mascotas.registrar_mascota(cliente.id_cliente, mascota_data)
        mascota = self.gestion_mascotas.listar_mascotas()[0]

        resultado = self.gestion_mascotas.eliminar_mascota(mascota.id_mascota)
        self.assertIn("eliminada con éxito", resultado)

        # Verificar que la mascota haya sido eliminada
        mascotas = self.gestion_mascotas.listar_mascotas()
        self.assertEqual(len(mascotas), 0)

    def test_eliminar_mascota_no_encontrada(self):
        resultado = self.gestion_mascotas.eliminar_mascota(9999)  # ID de mascota inexistente
        self.assertIn("No se encontró la mascota con ID", resultado)

    def test_eliminar_mascota_error(self):
        cliente_data = {
            'nombre_cliente': 'Laura García',
            'edad': 28,
            'dni': self.dni_unico,
            'direccion': 'Calle Prueba 456',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        cliente = self.gestion_clientes.buscar_cliente(dni=self.dni_unico)

        mascota_data = {
            'nombre_mascota': 'Rocky',
            'raza': 'Bulldog',
            'edad': 3,
            'afeccion': 'Ninguna',
            'estado': 'Vivo'
        }
        self.gestion_mascotas.registrar_mascota(cliente.id_cliente, mascota_data)
        mascota = self.gestion_mascotas.listar_mascotas()[0]

        with unittest.mock.patch.object(self.session, 'commit', side_effect=SQLAlchemyError("Error de SQLAlchemy")):
            resultado = self.gestion_mascotas.eliminar_mascota(mascota.id_mascota)
            self.assertIn("Error al eliminar la mascota", resultado)

    def test_listar_mascotas_exitoso(self):
        cliente_data = {
            'nombre_cliente': 'Pedro López',
            'edad': 35,
            'dni': self.dni_unico,
            'direccion': 'Avenida Principal 123',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        cliente = self.gestion_clientes.buscar_cliente(dni=self.dni_unico)

        mascota_data_1 = {
            'nombre_mascota': 'Fido',
            'raza': 'Labrador',
            'edad': 4,
            'afeccion': 'Ninguna',
            'estado': 'Vivo'
        }
        mascota_data_2 = {
            'nombre_mascota': 'Milo',
            'raza': 'Beagle',
            'edad': 2,
            'afeccion': 'Ninguna',
            'estado': 'Vivo'
        }

        self.gestion_mascotas.registrar_mascota(cliente.id_cliente, mascota_data_1)
        self.gestion_mascotas.registrar_mascota(cliente.id_cliente, mascota_data_2)

        mascotas = self.gestion_mascotas.listar_mascotas()
        self.assertEqual(len(mascotas), 2)
        self.assertEqual(mascotas[0].nombre_mascota, 'Fido')
        self.assertEqual(mascotas[1].nombre_mascota, 'Milo')

    def test_listar_mascotas_base_datos_vacia(self):
        mascotas = self.gestion_mascotas.listar_mascotas()
        self.assertEqual(len(mascotas), 0)

    def test_listar_mascotas_error(self):
        with unittest.mock.patch.object(self.session, 'query', side_effect=SQLAlchemyError("Error de SQLAlchemy")):
            with self.assertLogs(level='ERROR') as log:
                mascotas = self.gestion_mascotas.listar_mascotas()
                self.assertEqual(len(mascotas), 0)
                self.assertIn("Error de SQLAlchemy al listar las mascotas", log.output[-1])

    def test_buscar_mascota_por_nombre_encontrada(self):
        cliente_data = {
            'nombre_cliente': 'Pedro López',
            'edad': 35,
            'dni': self.dni_unico,
            'direccion': 'Avenida Principal 123',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        cliente = self.gestion_clientes.buscar_cliente(dni=self.dni_unico)

        mascota_data = {
            'nombre_mascota': 'Fido',
            'raza': 'Labrador',
            'edad': 4,
            'afeccion': 'Ninguna',
            'estado': 'Vivo'
        }
        self.gestion_mascotas.registrar_mascota(cliente.id_cliente, mascota_data)

        resultado = self.gestion_mascotas.buscar_mascota_por_nombre('Fido')
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['mascota'].nombre_mascota, 'Fido')

    def test_buscar_mascota_por_nombre_no_encontrada(self):
        resultado = self.gestion_mascotas.buscar_mascota_por_nombre('NoExistente')
        self.assertIsNone(resultado)

    def test_buscar_mascota_por_nombre_error(self):
        with unittest.mock.patch.object(self.session, 'query', side_effect=SQLAlchemyError("Error de SQLAlchemy")):
            with self.assertLogs(level='ERROR') as log:
                resultado = self.gestion_mascotas.buscar_mascota_por_nombre('ErrorMascota')
                self.assertIsNone(resultado)
                self.assertIn("Error de SQLAlchemy al buscar la mascota por nombre", log.output[-1])

    def test_marcar_mascota_como_fallecido_exitoso(self):
        cliente_data = {
            'nombre_cliente': 'José Martínez',
            'edad': 50,
            'dni': self.dni_unico,
            'direccion': 'Calle Central 45',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        cliente = self.gestion_clientes.buscar_cliente(dni=self.dni_unico)

        mascota_data = {
            'nombre_mascota': 'Toby',
            'raza': 'Pastor Alemán',
            'edad': 7,
            'afeccion': 'Ninguna',
            'estado': 'Vivo'
        }
        self.gestion_mascotas.registrar_mascota(cliente.id_cliente, mascota_data)

        resultado = self.gestion_mascotas.marcar_mascota_como_fallecido(cliente.id_cliente, 'Toby')
        self.assertIn("ha sido marcada como fallecida", resultado)

        mascota = self.gestion_mascotas.listar_mascotas()[0]
        self.assertEqual(mascota.estado, 'Fallecido')

    def test_marcar_mascota_como_fallecido_no_encontrada(self):
        resultado = self.gestion_mascotas.marcar_mascota_como_fallecido(9999, 'NoExistente')  # ID de cliente y nombre de mascota inexistentes
        self.assertIn("No se encontró la mascota", resultado)

    def test_marcar_mascota_como_fallecido_error(self):
        cliente_data = {
            'nombre_cliente': 'María López',
            'edad': 40,
            'dni': self.dni_unico,
            'direccion': 'Avenida Este 123',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        cliente = self.gestion_clientes.buscar_cliente(dni=self.dni_unico)

        mascota_data = {
            'nombre_mascota': 'Lola',
            'raza': 'Terrier',
            'edad': 3,
            'afeccion': 'Alergias',
            'estado': 'Vivo'
        }
        self.gestion_mascotas.registrar_mascota(cliente.id_cliente, mascota_data)

        with unittest.mock.patch.object(self.session, 'commit', side_effect=SQLAlchemyError("Error de SQLAlchemy")):
            resultado = self.gestion_mascotas.marcar_mascota_como_fallecido(cliente.id_cliente, 'Lola')
            self.assertIn("Error al marcar la mascota como fallecida", resultado)

if __name__ == '__main__':
    unittest.main()