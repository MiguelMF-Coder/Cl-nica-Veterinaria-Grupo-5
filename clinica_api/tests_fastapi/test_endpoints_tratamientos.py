import unittest
import tempfile
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport
from server import app 
from clinica.dbconfig import Base, get_db
from clinica_api.schemas import TratamientoCreate, TratamientoUpdate    
import os
import asyncio

# Configuración para la base de datos de pruebas
test_sqlite_url = "sqlite:///./test_tratamientos.db"
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

class TestTratamientos(unittest.IsolatedAsyncioTestCase):
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
        
        cliente_response = await self.client.post("/clientes/", json=self.cliente_data)
        if cliente_response.status_code != 200:
            raise Exception(f"Error al crear cliente: {cliente_response.text}")
        
        self.id_cliente = cliente_response.json()["id_cliente"]
        
        # Crear un tratamiento antes de cada prueba
        self.tratamiento_data = {
            "nombre_tratamiento": "Vacunación Canina",
            "descripcion": "Primera dosis de vacuna para perros",
            "precio": 50.0,
            "id_cliente": self.id_cliente
        }
        
        tratamiento_response = await self.client.post("/tratamientos/", json=self.tratamiento_data)
        if tratamiento_response.status_code != 200:
            raise Exception(f"Error al crear tratamiento: {tratamiento_response.text}")
        
        self.id_tratamiento = tratamiento_response.json()["id_tratamiento"]

    async def asyncTearDown(self):
        await self.client.aclose()


    async def test_exportar_tratamientos_a_json_endpoint(self):
        # Archivo temporal para exportación de JSON
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            temp_file_path = temp_file.name

        # Realizar la solicitud al endpoint
        response = await self.client.post("/tratamientos/exportar")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertIn("Tratamientos exportados", response.json()["message"])

        # Verificar que el archivo JSON no esté vacío
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            self.assertTrue(content, "El archivo JSON está vacío.")
            
            datos = json.loads(content)
            self.assertTrue(any(tratamiento['id_tratamiento'] == 1 for tratamiento in datos))

        # Limpieza del archivo de prueba
        os.remove(temp_file_path)

    async def test_dar_alta_tratamiento(self):
        nuevo_tratamiento = {
            "nombre_tratamiento": "Desparasitación Canina",
            "descripcion": "Tratamiento para desparasitar perros",
            "precio": 30.0,
            "id_cliente": self.id_cliente
        }
        
        response = await self.client.post("/tratamientos/", json=nuevo_tratamiento)
        if response.status_code != 200:
            raise Exception(f"Error al dar de alta tratamiento: {response.text}")
        
        data = response.json()
        self.assertEqual(data["nombre_tratamiento"], nuevo_tratamiento["nombre_tratamiento"])
        self.assertEqual(data["descripcion"], nuevo_tratamiento["descripcion"])

    async def test_dar_baja_tratamiento(self):
        response = await self.client.delete(f"/tratamientos/{self.tratamiento_data['nombre_tratamiento']}")
        if response.status_code != 200:
            raise Exception(f"Error al dar de baja tratamiento: {response.text}")
        
        data = response.json()
        self.assertIn("message", data)

    async def test_modificar_tratamiento(self):
        tratamiento_update = {
            "descripcion": "Actualización de la dosis de vacuna para perros"
        }
        
        response = await self.client.put(f"/tratamientos/{self.id_tratamiento}", json=tratamiento_update)
        if response.status_code != 200:
            raise Exception(f"Error al modificar tratamiento: {response.text}")
        
        data = response.json()
        self.assertEqual(data["descripcion"], tratamiento_update["descripcion"])

    async def test_obtener_datos_factura(self):
        response = await self.client.get(f"/tratamientos/factura/{self.id_tratamiento}")
        if response.status_code != 200:
            raise Exception(f"Error al obtener datos de factura: {response.text}")
        
        data = response.json()
        self.assertIn("cliente", data)
        self.assertIn("mascota", data)

    async def test_validar_tratamiento_Finalizada(self):
        response = await self.client.get(f"/tratamientos/validar/{self.id_tratamiento}")
        if response.status_code != 200:
            raise Exception(f"Error al validar tratamiento: {response.text}")
        
        data = response.json()
        self.assertIn("Finalizada", data)

    async def test_generar_factura(self):
        response = await self.client.get(f"/tratamientos/factura/generar/{self.id_tratamiento}")
        if response.status_code != 200:
            raise Exception(f"Error al generar factura: {response.text}")
        
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertTrue(os.path.exists("factura.pdf"))

if __name__ == "__main__":
    asyncio.run(unittest.main())
