import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from clinica.database import Base
from clinica.models.tabla_cliente import cliente as ClienteModel
from clinica.models.tabla_mascota import Mascota as MascotaModel
from clinica.services.gestion_clientes import GestionClientes

# Configuración de la base de datos en memoria para pruebas
@pytest.fixture(scope='module')
def db_session():
    engine = create_engine('sqlite:///:memory:', echo=False)
    Base.metadata.create_all(engine)  # Crea las tablas en la base de datos en memoria
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

def test_registrar_cliente_exitoso(db_session):
    gestion_clientes = GestionClientes(db_session)
    cliente_data = {
        'nombre_cliente': 'Juan Pérez',
        'edad': 30,
        'dni': '12345678A',
        'dirección': 'Calle Falsa 123',
        'telefono': 987654321
    }
    
    resultado = gestion_clientes.registrar_cliente(cliente_data)
    assert "registrado con éxito" in resultado

def test_registrar_cliente_duplicado(db_session):
    gestion_clientes = GestionClientes(db_session)
    cliente_data = {
        'nombre_cliente': 'Ana López',
        'edad': 25,
        'dni': '87654321B',
        'dirección': 'Calle Real 456',
        'telefono': 123456789
    }
    
    gestion_clientes.registrar_cliente(cliente_data)
    resultado = gestion_clientes.registrar_cliente(cliente_data)
    assert "ya está registrado" in resultado

def test_buscar_cliente_por_dni(db_session):
    gestion_clientes = GestionClientes(db_session)
    cliente_data = {
        'nombre_cliente': 'Carlos Martínez',
        'edad': 40,
        'dni': '11223344C',
        'dirección': 'Avenida Principal 789',
        'telefono': 112233445
    }
    
    gestion_clientes.registrar_cliente(cliente_data)
    cliente = gestion_clientes.buscar_cliente(dni='11223344C')
    assert cliente is not None
    assert cliente.dni == '11223344C'

def test_buscar_cliente_no_existente(db_session):
    gestion_clientes = GestionClientes(db_session)
    cliente = gestion_clientes.buscar_cliente(dni='99999999Z')
    assert cliente == "Cliente no encontrado."

def test_registrar_mascota_exitoso(db_session):
    gestion_clientes = GestionClientes(db_session)
    cliente_data = {
        'nombre_cliente': 'Luis Gómez',
        'edad': 35,
        'dni': '55667788D',
        'dirección': 'Calle Nueva 101',
        'telefono': 223344556
    }
    gestion_clientes.registrar_cliente(cliente_data)

    cliente = gestion_clientes.buscar_cliente(dni='55667788D')
    mascota_data = {
        'nombre_mascota': 'Max',
        'raza': 'Labrador',
        'edad': 3,
        'afeccion': 'Ninguna',
        'Estado': 'Vivo'
    }

    resultado = gestion_clientes.registrar_mascota(cliente.id_cliente, mascota_data)
    assert "registrada para el cliente" in resultado

def test_marcar_mascota_como_fallecido(db_session):
    gestion_clientes = GestionClientes(db_session)
    cliente_data = {
        'nombre_cliente': 'María Ruiz',
        'edad': 45,
        'dni': '33445566E',
        'dirección': 'Paseo del Prado 202',
        'telefono': 445566778
    }
    gestion_clientes.registrar_cliente(cliente_data)

    cliente = gestion_clientes.buscar_cliente(dni='33445566E')
    mascota_data = {
        'nombre_mascota': 'Luna',
        'raza': 'Golden Retriever',
        'edad': 5,
        'afeccion': 'Artritis',
        'Estado': 'Vivo'
    }
    gestion_clientes.registrar_mascota(cliente.id_cliente, mascota_data)

    resultado = gestion_clientes.marcar_mascota_como_fallecido(cliente.id_cliente, 'Luna')
    assert "ha sido marcada como fallecida" in resultado
