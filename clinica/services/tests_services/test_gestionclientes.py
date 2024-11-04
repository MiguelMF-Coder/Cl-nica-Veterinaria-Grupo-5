# test_gestionclientes.py

import sys
import os
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from clinica.dbconfig import Base
from clinica.models.tabla_cliente import Cliente as ClienteModel
from clinica.models.tabla_mascota import Mascota as MascotaModel
from clinica.services.gestion_clientes import GestionClientes

# Añadir la ruta de la carpeta raíz del proyecto al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

class TestGestionClientes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configuración de la base de datos en memoria para pruebas
        engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(engine)  # Crea todas las tablas necesarias en la base de datos en memoria
        Session = sessionmaker(bind=engine)
        cls.session = Session()

    @classmethod
    def tearDownClass(cls):
        # Cerrar la sesión y eliminar las tablas.
        cls.session.close()
        Base.metadata.drop_all(bind=cls.session.bind)

    def setUp(self):
        # Inicializa la clase de gestión de clientes para cada prueba
        self.gestion_clientes = GestionClientes(self.session)

    def test_registrar_cliente_exitoso(self):
        cliente_data = {
            'nombre_cliente': 'Juan Pérez',
            'edad': 30,
            'dni': '12345678A',
            'direccion': 'Calle Falsa 123',
            'telefono': 987654321
        }
        resultado = self.gestion_clientes.registrar_cliente(cliente_data)
        self.assertIn("registrado con éxito", resultado)

    def test_registrar_cliente_duplicado(self):
        cliente_data = {
            'nombre_cliente': 'Ana López',
            'edad': 25,
            'dni': '87654321B',
            'direccion': 'Calle Real 456',
            'telefono': 123456789
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        resultado = self.gestion_clientes.registrar_cliente(cliente_data)
        self.assertIn("ya está registrado", resultado)

    def test_buscar_cliente_por_dni(self):
        cliente_data = {
            'nombre_cliente': 'Carlos Martínez',
            'edad': 40,
            'dni': '11223344C',
            'direccion': 'Avenida Principal 789',
            'telefono': 112233445
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        cliente = self.gestion_clientes.buscar_cliente(dni='11223344C')
        self.assertIsNotNone(cliente)
        if cliente:
            self.assertEqual(cliente.dni, '11223344C')

    def test_buscar_cliente_no_existente(self):
        cliente = self.gestion_clientes.buscar_cliente(dni='99999999Z')
        self.assertIsNone(cliente)

    def test_registrar_mascota_exitoso(self):
        cliente_data = {
            'nombre_cliente': 'Luis Gómez',
            'edad': 35,
            'dni': '55667788D',
            'direccion': 'Calle Nueva 101',
            'telefono': 223344556
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        cliente = self.gestion_clientes.buscar_cliente(dni='55667788D')
        mascota_data = {
            'nombre_mascota': 'Max',
            'raza': 'Labrador',
            'edad': 3,
            'afeccion': 'Ninguna',
            'estado': 'Vivo'
        }
        resultado = self.gestion_clientes.registrar_mascota(cliente.id_cliente, mascota_data)
        self.assertIn("registrada para el cliente", resultado)

    def test_marcar_mascota_como_fallecido(self):
        cliente_data = {
            'nombre_cliente': 'María Ruiz',
            'edad': 45,
            'dni': '33445566E',
            'direccion': 'Paseo del Prado 202',
            'telefono': 445566778
        }
        self.gestion_clientes.registrar_cliente(cliente_data)
        cliente = self.gestion_clientes.buscar_cliente(dni='33445566E')
        mascota_data = {
            'nombre_mascota': 'Luna',
            'raza': 'Golden Retriever',
            'edad': 5,
            'afeccion': 'Artritis',
            'estado': 'Vivo'
        }
        self.gestion_clientes.registrar_mascota(cliente.id_cliente, mascota_data)
        resultado = self.gestion_clientes.marcar_mascota_como_fallecido(cliente.id_cliente, 'Luna')
        self.assertIn("ha sido marcada como fallecida", resultado)

if __name__ == '__main__':
    unittest.main()
