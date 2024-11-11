import unittest
import random
import uuid
import tempfile
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport
from clinica_api.server import app  
from clinica.dbconfig import Base, get_db
import asyncio

# Configuración para la base de datos de pruebas
test_sqlite_url = "sqlite:///./test_temp.db"
engine = create_engine(test_sqlite_url, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear las tablas en la base de datos de pruebas
Base.metadata.create_all(bind=engine)

# Dependencia de prueba para obtener la sesión de base de datos
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

class TestCitas(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        transport = ASGITransport(app=app)
        self.client = AsyncClient(transport=transport, base_url="http://testserver")
        
        # Registrar un cliente y una mascota de prueba
        nuevo_cliente = {
            "nombre_cliente": "Juan Perez",
            "edad": 30,
            "dni": f"{str(uuid.uuid4())[:8]}A",
            "direccion": "Calle Falsa 123",
            "telefono": f"{random.randint(600000000, 699999999)}"
        }

        cliente_response = await self.client.post("/clientes/", json=nuevo_cliente)
        if cliente_response.status_code != 200:
            raise Exception(f"Error al crear cliente: {cliente_response.text}")
        
        cliente_data = cliente_response.json()
        self.id_cliente = cliente_data.get("id_cliente")
        if not self.id_cliente:
            raise Exception("Error: La respuesta no contiene 'id_cliente'")

        nueva_mascota = {
            "nombre_mascota": "Firulais",
            "raza": "Labrador",
            "edad": 3,
            "afeccion": "Ninguna",
            "id_cliente": self.id_cliente
        }

        mascota_response = await self.client.post("/mascotas/", json=nueva_mascota)
        if mascota_response.status_code != 200:
            raise Exception(f"Error al crear mascota: {mascota_response.text}")
        
        mascota_data = mascota_response.json()
        self.id_mascota = mascota_data.get("id_mascota")
        if not self.id_mascota:
            raise Exception("Error: La respuesta no contiene 'id_mascota'")
        

        # Registrar un tratamiento de prueba
        nuevo_tratamiento = {
            "nombre_tratamiento": "Vacunación",
            "descripcion": "Vacuna contra la rabia",
            "precio": 50,
            "estado": "Activo",
            "id_cliente": self.id_cliente
        }
        tratamiento_response = await self.client.post("/tratamientos/", json=nuevo_tratamiento)
        if tratamiento_response.status_code != 200:
            raise Exception(f"Error al crear tratamiento: {tratamiento_response.text}")
        tratamiento_data = tratamiento_response.json()
        self.id_tratamiento = tratamiento_data.get("id_tratamiento")
    
    async def asyncTearDown(self):
        await self.client.aclose()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)


    async def test_exportar_citas_a_json_endpoint(self):
        # Usar un archivo temporal para la exportación de JSON
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            temp_file_path = temp_file.name

        # Realizar la solicitud al endpoint para exportar citas
        response = await self.client.post("/citas/exportar")

        # Verificar que la respuesta es exitosa
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertIn("Citas exportadas", response.json()["message"])

        # Verificar que el archivo no esté vacío y contenga datos de citas
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            self.assertTrue(content, "El archivo JSON está vacío.")
            
            datos = json.loads(content)
            self.assertTrue(any(cita['id_cita'] == 1 for cita in datos))

        # Eliminar el archivo temporal
        os.remove(temp_file_path)

    async def test_registrar_cita(self):
        nueva_cita = {
            "id_mascota": self.id_mascota,
            "id_cliente": self.id_cliente,
            "id_tratamiento": self.id_tratamiento,
            "fecha": "2024-11-10 10:00:00",
            "descripcion": "Cita de vacunación"
        }

        response = await self.client.post("/citas/", json=nueva_cita)

        # Verifica si la respuesta es exitosa (200 o 201)
        if response.status_code not in (200, 201):
            raise Exception(f"Error al registrar cita: {response.text}")

        data = response.json()

        # Comprueba que id_cita esté en la respuesta
        self.id_cita = data.get("id_cita")
        if not self.id_cita:
            raise Exception("Error: La respuesta no contiene 'id_cita'")

        # Validación de los datos devueltos
        self.assertEqual(data["id_mascota"], nueva_cita["id_mascota"])
        self.assertEqual(data["descripcion"], nueva_cita["descripcion"])
        self.assertEqual(data["id_cliente"], nueva_cita["id_cliente"])  # Validación de cliente
        self.assertEqual(data["fecha"], nueva_cita["fecha"])  # Validación de fecha


    async def test_ver_todas_las_citas(self):
        response = await self.client.get("/citas/")
        if response.status_code != 200:
            raise Exception(f"Error al listar citas: {response.text}")

        data = response.json()
        self.assertIsInstance(data, list)

    async def test_buscar_cita(self):
        await self.test_registrar_cita()
        response = await self.client.get(f"/citas/buscar/{self.id_mascota}/{self.id_cliente}")
        if response.status_code != 200:
            raise Exception(f"Error al buscar cita: {response.text}")

        data = response.json()
        self.assertEqual(data.get("id_mascota"), self.id_mascota)
        self.assertEqual(data.get("id_cliente"), self.id_cliente)

    async def test_modificar_cita(self):
        await self.test_registrar_cita()
        cita_update = {
            "descripcion": "Cita de chequeo general"
        }

        response = await self.client.put(f"/citas/{self.id_cita}", json=cita_update)
        if response.status_code != 200:
            raise Exception(f"Error al modificar cita: {response.text}")

        data = response.json()
        self.assertEqual(data.get("descripcion"), cita_update["descripcion"])

    async def test_cancelar_cita(self):
        await self.test_registrar_cita()
        response = await self.client.delete(f"/citas/{self.id_cita}")
        if response.status_code != 200:
            raise Exception(f"Error al cancelar cita: {response.text}")

        data = response.json()
        self.assertIn("message", data)

    async def test_finalizar_cita(self):
        await self.test_registrar_cita()
        tratamientos_realizados = "Vacunación y chequeo general"
        metodo_pago = "Tarjeta"
        response = await self.client.put(f"/citas/finalizar/{self.id_cita}", params={"tratamientos_realizados": tratamientos_realizados, "metodo_pago": metodo_pago})
        if response.status_code != 200:
            raise Exception(f"Error al finalizar cita: {response.text}")

        data = response.json()
        self.assertIn("message", data)

if __name__ == "__main__":
    asyncio.run(unittest.main())
