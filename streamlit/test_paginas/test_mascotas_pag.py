import unittest
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport
from server import app  
from clinica.dbconfig import Base, get_db
from clinica_api.schemas import MascotaCreate, MascotaUpdate    
import os
import asyncio

# Configuración de pruebas
test_sqlite_url = "sqlite:///./test_mascotas.db"
engine = create_engine(test_sqlite_url, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

class TestMascotas(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        transport = ASGITransport(app=app)
        self.client = AsyncClient(transport=transport, base_url="http://testserver")
        
        # Crear cliente y mascota de prueba
        self.cliente_data = {
            "nombre_cliente": "Juan Perez",
            "dni": "12345678A",
            "telefono": "600123456",
            "direccion": "Calle Falsa 123",
            "edad": 30
        }
        cliente_response = await self.client.post("/clientes/", json=self.cliente_data)
        self.assertEqual(cliente_response.status_code, 200)
        self.id_cliente = cliente_response.json()["id_cliente"]

        self.mascota_data = {
            "nombre_mascota": "Firulais",
            "raza": "Labrador",
            "edad": 3,
            "afeccion": "Ninguna",
            "id_cliente": self.id_cliente
        }
        mascota_response = await self.client.post(f"/mascotas/?id_cliente={self.id_cliente}", json=self.mascota_data)
        self.assertEqual(mascota_response.status_code, 200)
        self.id_mascota = mascota_response.json()["id_mascota"]

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_registrar_mascota(self):
        nueva_mascota = {
            "nombre_mascota": "Rex",
            "raza": "Golden Retriever",
            "edad": 2,
            "afeccion": "Ninguna",
            "id_cliente": self.id_cliente
        }
        response = await self.client.post(f"/mascotas/?id_cliente={self.id_cliente}", json=nueva_mascota)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["nombre_mascota"], nueva_mascota["nombre_mascota"])
        self.assertEqual(data["raza"], nueva_mascota["raza"])

    async def test_listar_mascotas(self):
        response = await self.client.get("/mascotas/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    async def test_modificar_mascota(self):
        mascota_update = {
            "afeccion": "Leve dermatitis"
        }
        response = await self.client.put(f"/mascotas/{self.id_mascota}", json=mascota_update)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["afeccion"], mascota_update["afeccion"])

    async def test_eliminar_mascota(self):
        response = await self.client.delete(f"/mascotas/{self.id_mascota}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)

    async def test_exportar_mascotas(self):
        response = await self.client.post("/mascotas/exportar")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("Mascotas exportadas a", data["message"])
        self.assertTrue(os.path.exists('clinica/data/tabla_mascotas.json'))

    async def test_buscar_mascota_por_nombre(self):
        nombre_mascota = self.mascota_data["nombre_mascota"]
        response = await self.client.get(f"/mascotas/buscar_por_nombre/{nombre_mascota}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["nombre_mascota"], nombre_mascota)

    async def test_marcar_mascota_como_fallecido(self):
        nombre_mascota = self.mascota_data["nombre_mascota"]
        response = await self.client.put(f"/mascotas/fallecido/{self.id_cliente}/{nombre_mascota}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)

    async def test_filtros_mascota(self):
        # Test filtro por nombre
        response = await self.client.get("/mascotas/", params={"nombre": "Firulais"})
        self.assertEqual(response.status_code, 200)
        
        # Test filtro por raza
        response = await self.client.get("/mascotas/", params={"raza": "Labrador"})
        self.assertEqual(response.status_code, 200)
        
        # Test filtro por estado
        response = await self.client.get("/mascotas/", params={"estado": "Vivo"})
        self.assertEqual(response.status_code, 200)

    async def test_validaciones_formulario(self):
        mascota_invalida = {
            "nombre_mascota": "",  # Nombre vacío
            "raza": "Labrador",
            "edad": 3,
            "id_cliente": self.id_cliente
        }
        response = await self.client.post(f"/mascotas/?id_cliente={self.id_cliente}", json=mascota_invalida)
        self.assertEqual(response.status_code, 422)

if __name__ == "__main__":
    asyncio.run(unittest.main())