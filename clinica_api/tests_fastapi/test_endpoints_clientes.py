import unittest
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport
from clinica_api.server import app  
from clinica.dbconfig import Base, get_db
from clinica_api.schemas import ClienteCreate, ClienteUpdate
import os
import asyncio

# Configuración para la base de datos de pruebas
test_sqlite_url = "sqlite:///./test_clientes.db"
engine = create_engine(test_sqlite_url, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear las tablas en la base de datos de pruebas
Base.metadata.create_all(bind=engine)

# Dependencia de prueba para obtener la sesión de la base de datos
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

class TestClientes(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        Base.metadata.drop_all(bind=engine)  # Elimina todas las tablas
        Base.metadata.create_all(bind=engine)  # Crea las tablas nuevamente
        transport = ASGITransport(app=app)
        self.client = AsyncClient(transport=transport, base_url="http://testserver")
        
        # Crear un cliente antes de cada prueba
        self.cliente_data = {
            "nombre_cliente": "Juan Perez",
            "dni": "12345678A",
            "telefono": "600123456",
            "direccion": "Calle Falsa 123",
            "edad": 30
        }
        
        response = await self.client.post("/clientes/", json=self.cliente_data)
        if response.status_code != 200:
            raise Exception(f"Error al crear cliente: {response.text}")
        
        self.id_cliente = response.json()["id_cliente"]

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_registrar_cliente(self):
        nuevo_cliente = {
            "nombre_cliente": "Ana Gomez",
            "dni": "87654321B",
            "telefono": "600654321",
            "direccion": "Avenida Siempre Viva 742",
            "edad": 25
        }
        
        response = await self.client.post("/clientes/", json=nuevo_cliente)
        if response.status_code != 200:
            raise Exception(f"Error al registrar cliente: {response.text}")
        
        data = response.json()
        self.assertEqual(data["nombre_cliente"], nuevo_cliente["nombre_cliente"])
        self.assertEqual(data["dni"], nuevo_cliente["dni"])

    async def test_listar_clientes(self):
        response = await self.client.get("/clientes/")
        if response.status_code != 200:
            raise Exception(f"Error al listar clientes: {response.text}")
        
        data = response.json()
        self.assertIsInstance(data, list)

    async def test_buscar_cliente(self):
        response = await self.client.get(f"/clientes/buscar/{self.cliente_data['dni']}")
        if response.status_code != 200:
            raise Exception(f"Error al buscar cliente: {response.text}")
        
        data = response.json()
        self.assertEqual(data["dni"], self.cliente_data["dni"])

    async def test_modificar_cliente(self):
        cliente_update = {
            "telefono": "600987654"
        }
        
        response = await self.client.put(f"/clientes/{self.id_cliente}", json=cliente_update)
        if response.status_code != 200:
            raise Exception(f"Error al modificar cliente: {response.text}")
        
        data = response.json()
        self.assertEqual(data["telefono"], cliente_update["telefono"])

    async def test_eliminar_cliente(self):
        response = await self.client.delete(f"/clientes/{self.id_cliente}")
        if response.status_code != 200:
            raise Exception(f"Error al eliminar cliente: {response.text}")
        
        data = response.json()
        self.assertIn("message", data)

    async def test_exportar_clientes(self):
        response = await self.client.post("/clientes/exportar")
        if response.status_code != 200:
            raise Exception(f"Error al exportar clientes: {response.text}")
        
        data = response.json()
        self.assertIn("Clientes exportados a", data["message"])
        self.assertTrue(os.path.exists('clinica/data/tabla_clientes.json'))

    async def test_buscar_cliente_por_nombre(self):
        nombre_cliente = self.cliente_data["nombre_cliente"]
        response = await self.client.get(f"/clientes/buscar_por_nombre/{nombre_cliente}")
        if response.status_code != 200:
            raise Exception(f"Error al buscar cliente por nombre: {response.text}")
        
        data = response.json()
        self.assertEqual(data["cliente"]["nombre_cliente"], nombre_cliente)

if __name__ == "__main__":
    asyncio.run(unittest.main())
