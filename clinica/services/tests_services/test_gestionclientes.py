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


# Añadir la ruta de la carpeta raíz del proyecto al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

class TestGestionClientes(unittest.TestCase):
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

    def test_exportar_clientes_a_json_exitoso(self):
        cliente_data = {
            'nombre_cliente': 'Pedro Sánchez',
            'edad': 50,
            'dni': self.dni_unico,
            'direccion': 'Calle Ejemplo 303',
            'telefono': self.telefono_unico
        }   
        resultado = self.gestion_clientes.registrar_cliente(cliente_data)
        
        # Verificar que el cliente se ha registrado correctamente
        self.assertIsInstance(resultado, ClienteModel, "Error: No se pudo registrar el cliente antes de exportar.")
        
        # Comprobar que el cliente esté realmente en la base de datos
        cliente_en_bd = self.session.query(ClienteModel).filter_by(dni=self.dni_unico).first()
        self.assertIsNotNone(cliente_en_bd, "Error: Cliente no encontrado en la base de datos después del registro.")
        
        # Usar un archivo temporal para la prueba
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            temp_file_path = temp_file.name

        # Llama a la función para exportar clientes a JSON
        self.gestion_clientes.exportar_clientes_a_json(temp_file_path)

        # Verificar que el archivo no esté vacío antes de cargar el JSON
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()  # Lee el contenido como texto
            self.assertTrue(content, "El archivo JSON está vacío.")  # Verifica que no esté vacío
            
            # Ahora, convierte el contenido en JSON y realiza las aserciones
            datos = json.loads(content)
            print("Datos exportados:", datos)  # Depuración: Imprimir datos exportados
            self.assertTrue(any(cliente['dni'] == self.dni_unico for cliente in datos))

        # Limpieza del archivo de prueba
        os.remove(temp_file_path)


    def test_exportar_clientes_a_json_error(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            temp_file_path = temp_file.name
        
        with unittest.mock.patch('builtins.open', side_effect=OSError("Error de acceso")):
            with self.assertLogs(level='ERROR') as log:
                self.gestion_clientes.exportar_clientes_a_json(temp_file_path)
                self.assertIn("Error al exportar clientes a JSON", log.output[-1])


    def test_registrar_cliente_exitoso(self):
        cliente_data = {
            'nombre_cliente': 'Juan Pérez',
            'edad': 30,
            'dni': self.dni_unico,
            'direccion': 'Calle Falsa 123',
            'telefono': self.telefono_unico
        }
        
        resultado = self.gestion_clientes.registrar_cliente(cliente_data)
        
        # Si el resultado es una instancia, verifica sus atributos
        if isinstance(resultado, ClienteModel):
            self.assertEqual(resultado.nombre_cliente, cliente_data['nombre_cliente'])
            self.assertEqual(resultado.dni, cliente_data['dni'])
            self.assertEqual(resultado.direccion, cliente_data['direccion'])
        else:
            # Si hay un error, verifica el mensaje
            self.fail(f"Error en el registro del cliente: {resultado.get('error', 'Error desconocido')}")



    def test_registrar_cliente_duplicado(self):
        cliente_data = {
            'nombre_cliente': 'Ana López',
            'edad': 25,
            'dni': self.dni_unico,
            'direccion': 'Calle Real 456',
            'telefono': self.telefono_unico
        }
        
        # Primero registra el cliente
        self.gestion_clientes.registrar_cliente(cliente_data)
        
        # Intenta registrar el cliente duplicado
        resultado = self.gestion_clientes.registrar_cliente(cliente_data)

        # Verifica si `resultado` es un diccionario o una cadena y ajusta la verificación
        if isinstance(resultado, dict):
            self.assertIn("ya registrado", resultado.get('error', ''))
        else:
            self.assertIn("ya registrado", resultado)


    def test_registrar_cliente_integrity_error(self):
        with unittest.mock.patch('clinica.services.gestion_clientes.Session.commit', side_effect=IntegrityError('mock', 'mock', 'mock')):
            cliente_data = {
                'nombre_cliente': 'Juan Carlos',
                'edad': 33,
                'dni': self.dni_unico,
                'direccion': 'Calle Luna 12',
                'telefono': self.telefono_unico
            }
            resultado = self.gestion_clientes.registrar_cliente(cliente_data)
            
            # Verificar si el mensaje de error de integridad está en el resultado, ya sea string o dict
            if isinstance(resultado, str):
                self.assertIn("Error: No se pudo registrar el cliente debido a un problema de integridad", resultado)
            elif isinstance(resultado, dict) and 'error' in resultado:
                self.assertIn("Error: No se pudo registrar el cliente debido a un problema de integridad", resultado['error'])


    def test_registrar_cliente_error_general(self):
        # Simula un error inesperado al hacer commit en la base de datos
        with unittest.mock.patch('clinica.services.gestion_clientes.Session.commit', side_effect=Exception("Error inesperado")):
            cliente_data = {
                'nombre_cliente': 'Luis Torres',
                'edad': 40,
                'dni': self.dni_unico,
                'direccion': 'Calle Sol 23',
                'telefono': self.telefono_unico
            }
            
            resultado = self.gestion_clientes.registrar_cliente(cliente_data)

            # Verifica si `resultado` es un diccionario o una cadena y ajusta la verificación
            if isinstance(resultado, dict):
                self.assertIn("Ocurrió un error inesperado al registrar el cliente", resultado.get('error', ''))
            else:
                self.assertIn("Ocurrió un error inesperado al registrar el cliente", resultado)

    def test_modificar_cliente_exitoso(self):
        cliente_data = {
            'nombre_cliente': 'Laura García',
            'edad': 28,
            'dni': self.dni_unico,
            'direccion': 'Calle Prueba 404',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        #self.session.commit()

        # Buscar al cliente directamente en la base de datos
        cliente = self.session.query(ClienteModel).filter_by(dni=self.dni_unico).first()
        nuevos_datos = {
            'direccion': 'Avenida Nueva 505',
            'telefono': self.telefono_unico
        }
        resultado = self.gestion_clientes.modificar_cliente(cliente.id_cliente, nuevos_datos)
        #self.session.commit()
        self.assertIn("modificado con éxito", resultado)

        # Verificar que los cambios se realizaron
        cliente_actualizado = self.session.query(ClienteModel).filter_by(dni=self.dni_unico).first()
        self.assertEqual(cliente_actualizado.direccion, 'Avenida Nueva 505')
        self.assertEqual(cliente_actualizado.telefono, self.telefono_unico)


    def test_modificar_cliente_no_encontrado(self):
        resultado = self.gestion_clientes.modificar_cliente(9999, {'direccion': 'Nueva Dirección'})
        #self.session.commit()
        self.assertIn("No se encontró el cliente con ID", resultado)

    def test_modificar_cliente_error(self):
        cliente_data = {
            'nombre_cliente': 'Laura Cordero',
            'edad': 28,
            'dni': self.dni_unico,
            'direccion': 'Calle Prueba 404',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        cliente = self.gestion_clientes.buscar_cliente(dni=self.dni_unico)
        with unittest.mock.patch('clinica.services.gestion_clientes.Session.commit', side_effect=SQLAlchemyError("Error de SQLAlchemy")):
            resultado = self.gestion_clientes.modificar_cliente(cliente.id_cliente, {'direccion': 'Nueva Dirección'})
            #self.session.commit()
            self.assertIn("Error al modificar el cliente", resultado)

    def test_eliminar_cliente_exitoso(self):
        cliente_data = {
            'nombre_cliente': 'Carlos Martín',
            'edad': 40,
            'dni': self.dni_unico,
            'direccion': 'Calle Ejemplo 123',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        self.session.commit()

        # Buscar al cliente directamente en la base de datos
        cliente = self.session.query(ClienteModel).filter_by(dni=self.dni_unico).first()
        resultado = self.gestion_clientes.eliminar_cliente(cliente.id_cliente)
        self.session.commit()
        self.assertIn("eliminado con éxito", resultado)

        # Verificar que el cliente ya no está en la base de datos
        cliente_eliminado = self.session.query(ClienteModel).filter_by(dni=self.dni_unico).first()
        self.assertIsNone(cliente_eliminado)


    def test_eliminar_cliente_no_encontrado(self):
        resultado = self.gestion_clientes.eliminar_cliente(9999)
        self.assertIn("No se encontró el cliente con ID", resultado)

    def test_eliminar_cliente_error(self):
        cliente_data = {
            'nombre_cliente': 'Alberto García',
            'edad': 28,
            'dni': self.dni_unico,
            'direccion': 'Calle Prueba 404',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        self.session.commit()

        # Buscar al cliente directamente en la base de datos
        cliente = self.session.query(ClienteModel).filter_by(dni=self.dni_unico).first()

        # Simular un error de SQLAlchemy al hacer commit
        with unittest.mock.patch('clinica.services.gestion_clientes.Session.commit', side_effect=SQLAlchemyError("Error de SQLAlchemy")):
            resultado = self.gestion_clientes.eliminar_cliente(cliente.id_cliente)
            self.assertIn("Error al eliminar el cliente", resultado)


    def test_buscar_cliente_por_nombre_encontrado(self):
        cliente_data = {
            'nombre_cliente': 'Pablo Gil',
            'edad': 30,
            'dni': self.dni_unico,
            'direccion': 'Calle Falsa 123',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        self.session.commit()

        resultado = self.gestion_clientes.buscar_cliente_por_nombre('Pablo')
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['cliente'].nombre_cliente, 'Pablo Gil')
        self.assertEqual(resultado['cliente'].dni, self.dni_unico)

    def test_buscar_cliente_por_nombre_multiples_coincidencias(self):
        cliente_data_1 = {
            'nombre_cliente': 'Luis Fernández',
            'edad': 28,
            'dni': self.dni_unico,
            'direccion': 'Calle Norte 100',
            'telefono': self.telefono_unico
        }
        cliente_data_2 = {
            'nombre_cliente': 'Luis Borro',
            'edad': 35,
            'dni': self.dni_unico,
            'direccion': 'Avenida Sur 200',
            'telefono': self.telefono_unico
        }
        self.gestion_clientes.registrar_cliente(cliente_data_1)
        self.session.commit()
        self.gestion_clientes.registrar_cliente(cliente_data_2)
        self.session.commit()
        
        with unittest.mock.patch('builtins.input', return_value='1'):
            resultado = self.gestion_clientes.buscar_cliente_por_nombre('Luis')
            self.assertIsNotNone(resultado)
            self.assertEqual(resultado['cliente'].nombre_cliente, 'Luis Fernández')

    def test_buscar_cliente_por_nombre_no_encontrado(self):
        resultado = self.gestion_clientes.buscar_cliente_por_nombre('NoExistente')
        self.assertIsNone(resultado)

    def test_buscar_cliente_por_nombre_error(self):
        with unittest.mock.patch('clinica.services.gestion_clientes.Session.query', side_effect=SQLAlchemyError("Error de SQLAlchemy")):
            resultado = self.gestion_clientes.buscar_cliente_por_nombre('ErrorCliente')
            self.assertIsNone(resultado)

    def test_listar_clientes_exitoso(self):
        cliente_data_1 = {
            'nombre_cliente': 'Pedro Gómez',
            'edad': 34,
            'dni': f'12345678{random.randint(0, 4)}',
            'direccion': 'Calle Prueba 123',
            'telefono': random.randint(600000000, 650000000)
        }
        cliente_data_2 = {
            'nombre_cliente': 'Laura Pérez',
            'edad': 29,
            'dni': f'12345679{random.randint(5, 9)}',
            'direccion': 'Avenida Prueba 456',
            'telefono': random.randint(650000001, 699999999)
                            }
        
        self.gestion_clientes.registrar_cliente(cliente_data_1)
        self.gestion_clientes.registrar_cliente(cliente_data_2)
        self.session.commit()  # Asegúrate de hacer commit aquí

        clientes = self.gestion_clientes.listar_clientes()
        self.assertEqual(len(clientes), 2)
        self.assertEqual(clientes[0].nombre_cliente, 'Pedro Gómez')
        self.assertEqual(clientes[1].nombre_cliente, 'Laura Pérez')

    def test_listar_clientes_base_datos_vacia(self):
        clientes = self.gestion_clientes.listar_clientes()
        self.assertEqual(len(clientes), 0)

    def test_listar_clientes_error(self):
        with unittest.mock.patch('clinica.services.gestion_clientes.Session.query', side_effect=SQLAlchemyError("Error de SQLAlchemy")):
            clientes = self.gestion_clientes.listar_clientes()
            self.assertEqual(len(clientes), 0)

    