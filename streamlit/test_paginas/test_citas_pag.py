import unittest
import random
import uuid
import tempfile
import os
import sys
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient, ASGITransport
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from server import app
from clinica.dbconfig import Base, get_db
import asyncio

# Configuración para la base de datos de pruebas
test_sqlite_url = "sqlite:///./test_temp.db"
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

class TestCitas(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        transport = ASGITransport(app=app)
        self.client = AsyncClient(transport=transport, base_url="http://testserver")
        self.id_cliente = await self.crear_cliente()
        self.id_mascota = await self.crear_mascota(self.id_cliente)
        self.id_tratamiento = await self.crear_tratamiento(self.id_cliente)

    async def crear_cliente(self):
        numeros_dni = str(random.randint(10000000, 99999999))
        letra_dni = random.choice('TRWAGMYFPDXBNJZSQVHLCKE')
        dni_valido = f"{numeros_dni}{letra_dni}"
        telefono_valido = f"6{str(random.randint(0, 99999999)).zfill(8)}"

        nuevo_cliente = {
            "nombre_cliente": "Juan Perez",
            "edad": 30,
            "dni": dni_valido,
            "direccion": "Calle Falsa 123",
            "telefono": telefono_valido
        }

        cliente_response = await self.client.post("/clientes/", json=nuevo_cliente)
        assert cliente_response.status_code == 201
        return cliente_response.json()["id_cliente"]

    async def crear_mascota(self, id_cliente):
        nueva_mascota = {
            "nombre_mascota": "Firulais",
            "raza": "Labrador",
            "edad": 3,
            "afeccion": "Ninguna",
            "id_cliente": id_cliente
        }

        mascota_response = await self.client.post("/mascotas/", json=nueva_mascota)
        assert mascota_response.status_code == 201
        return mascota_response.json()["id_mascota"]

    async def crear_tratamiento(self, id_cliente):
        tratamiento_unico = f"Vacunación-{uuid.uuid4()}"
        nuevo_tratamiento = {
            "nombre_tratamiento": tratamiento_unico,
            "descripcion": "Vacuna contra la rabia",
            "precio": 50,
            "estado": "Activo",
            "id_cliente": id_cliente
        }

        tratamiento_response = await self.client.post("/tratamientos/", json=nuevo_tratamiento)
        assert tratamiento_response.status_code == 201
        return tratamiento_response.json()["id_tratamiento"]

    async def test_exportar_citas_a_json(self):
        await self.test_registrar_cita()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, 'citas_test.json')
            response = await self.client.post("/citas/exportar")
            
            self.assertEqual(response.status_code, 200)
            response_data = response.json()
            self.assertIn("message", response_data)
            self.assertIn("Citas exportadas", response_data["message"])
            
            ruta_exportada = response_data.get("path")
            if os.path.exists(ruta_exportada):
                with open(ruta_exportada, 'r') as src, open(temp_file, 'w') as dst:
                    content = src.read()
                    dst.write(content)
                    
                with open(temp_file, 'r') as f:
                    content = f.read().strip()
                    self.assertTrue(content)
                    datos = json.loads(content)
                    self.assertIsInstance(datos, list)
                    self.assertTrue(len(datos) > 0)
                    self.assertTrue(
                        any(cita.get('id_cita') == self.id_cita for cita in datos)
                    )

    async def test_registrar_cita(self):
        nueva_cita = {
            "id_mascota": self.id_mascota,
            "id_cliente": self.id_cliente,
            "id_tratamiento": self.id_tratamiento,
            "fecha": datetime.now().isoformat(),
            "descripcion": "Cita de vacunación"
        }

        response = await self.client.post("/citas/", json=nueva_cita)
        self.assertIn(response.status_code, (200, 201))

        data = response.json()
        self.id_cita = data.get("id_cita")
        self.assertTrue(self.id_cita)
        
        self.assertEqual(data["id_mascota"], nueva_cita["id_mascota"])
        self.assertEqual(data["descripcion"], nueva_cita["descripcion"])
        self.assertEqual(data["id_cliente"], nueva_cita["id_cliente"])
        self.assertEqual(data["fecha"], nueva_cita["fecha"])

    async def test_ver_todas_las_citas(self):
        response = await self.client.get("/citas/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    async def test_buscar_cita(self):
        await self.test_registrar_cita()
        response = await self.client.get(f"/citas/buscar/{self.id_mascota}/{self.id_cliente}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id_mascota"], self.id_mascota)
        self.assertEqual(data["id_cliente"], self.id_cliente)

    async def test_modificar_cita(self):
        await self.test_registrar_cita()
        cita_update = {"descripcion": "Cita de chequeo general"}
        response = await self.client.put(f"/citas/{self.id_cita}", json=cita_update)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["descripcion"], cita_update["descripcion"])

    async def test_cancelar_cita(self):
        await self.test_registrar_cita()
        response = await self.client.delete(f"/citas/{self.id_cita}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)

    async def test_finalizar_cita(self):
        await self.test_registrar_cita()
        tratamientos_realizados = "Vacunación y chequeo general"
        metodo_pago = "Tarjeta"
        
        response = await self.client.put(
            f"/citas/finalizar/{self.id_cita}", 
            params={"tratamientos_realizados": tratamientos_realizados, "metodo_pago": metodo_pago}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Cita finalizada con éxito")

if __name__ == "__main__":
    asyncio.run(unittest.main())