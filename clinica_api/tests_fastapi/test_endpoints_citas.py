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

        # Inicializar cliente HTTP
        transport = ASGITransport(app=app)
        self.client = AsyncClient(transport=transport, base_url="http://testserver")

        # Crear cliente
        self.id_cliente = await self.crear_cliente()

        # Crear mascota asociada al cliente
        self.id_mascota = await self.crear_mascota(self.id_cliente)

        # Crear tratamiento único asociado al cliente
        self.id_tratamiento = await self.crear_tratamiento(self.id_cliente)

    async def crear_cliente(self):
        # Generar un DNI válido
        numeros_dni = str(random.randint(10000000, 99999999))
        letra_dni = random.choice('TRWAGMYFPDXBNJZSQVHLCKE')
        dni_valido = f"{numeros_dni}{letra_dni}"

        # Generar un número de teléfono válido
        numero_aleatorio = str(random.randint(0, 99999999)).zfill(8)
        telefono_valido = f"6{numero_aleatorio}"

        nuevo_cliente = {
            "nombre_cliente": "Juan Perez",
            "edad": 30,
            "dni": dni_valido,
            "direccion": "Calle Falsa 123",
            "telefono": telefono_valido
        }

        cliente_response = await self.client.post("/clientes/", json=nuevo_cliente)
        assert cliente_response.status_code == 201, f"Error al crear cliente: {cliente_response.text}"

        cliente_data = cliente_response.json()
        id_cliente = cliente_data.get("id_cliente")
        assert id_cliente is not None, "Error: La respuesta no contiene 'id_cliente'"

        return id_cliente

    async def crear_mascota(self, id_cliente):
        nueva_mascota = {
            "nombre_mascota": "Firulais",
            "raza": "Labrador",
            "edad": 3,
            "afeccion": "Ninguna",
            "id_cliente": id_cliente
        }

        mascota_response = await self.client.post("/mascotas/", json=nueva_mascota)
        assert mascota_response.status_code == 201, f"Error al crear mascota: {mascota_response.text}"

        mascota_data = mascota_response.json()
        id_mascota = mascota_data.get("id_mascota")
        assert id_mascota is not None, "Error: La respuesta no contiene 'id_mascota'"

        return id_mascota

    async def crear_tratamiento(self, id_cliente):
        # Usar un nombre único para el tratamiento
        tratamiento_unico = f"Vacunación-{uuid.uuid4()}"

        nuevo_tratamiento = {
            "nombre_tratamiento": tratamiento_unico,
            "descripcion": "Vacuna contra la rabia",
            "precio": 50,
            "estado": "Activo",
            "id_cliente": id_cliente
        }

        tratamiento_response = await self.client.post("/tratamientos/", json=nuevo_tratamiento)
        assert tratamiento_response.status_code == 201, f"Error al crear tratamiento: {tratamiento_response.text}"

        tratamiento_data = tratamiento_response.json()
        id_tratamiento = tratamiento_data.get("id_tratamiento")
        assert id_tratamiento is not None, "Error: La respuesta no contiene 'id_tratamiento'"

        return id_tratamiento

    async def test_exportar_citas_a_json_endpoint(self):
        """Test para verificar la exportación de citas a JSON."""
        # Primero registramos una cita para asegurar que hay datos
        await self.test_registrar_cita()
        
        # Crear directorio temporal para el test
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, 'citas_test.json')
            
            # Realizar la solicitud al endpoint
            response = await self.client.post("/citas/exportar")
            
            # Verificar respuesta exitosa
            self.assertEqual(response.status_code, 200)
            response_data = response.json()
            self.assertIn("message", response_data)
            self.assertIn("Citas exportadas", response_data["message"])
            
            # Copiar el archivo exportado al directorio temporal
            ruta_exportada = response_data.get("path")
            if os.path.exists(ruta_exportada):
                with open(ruta_exportada, 'r') as src, open(temp_file, 'w') as dst:
                    content = src.read()
                    dst.write(content)
                    
                # Verificar contenido del archivo
                with open(temp_file, 'r') as f:
                    content = f.read().strip()
                    self.assertTrue(content, "El archivo JSON está vacío")
                    
                    # Verificar que el JSON es válido y contiene datos
                    datos = json.loads(content)
                    self.assertIsInstance(datos, list, "El contenido no es una lista válida")
                    self.assertTrue(len(datos) > 0, "No hay citas en el archivo exportado")
                    
                    # Verificar que la cita que creamos está en el archivo
                    self.assertTrue(
                        any(cita.get('id_cita') == self.id_cita for cita in datos),
                        "La cita creada no se encuentra en el archivo exportado"
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
        
        response = await self.client.put(
            f"/citas/finalizar/{self.id_cita}", 
            params={"tratamientos_realizados": tratamientos_realizados, "metodo_pago": metodo_pago}
        )
        
        if response.status_code != 200:
            raise Exception(f"Error al finalizar cita: {response.text}")

        data = response.json()
        self.assertEqual(data.get("message"), "Cita finalizada con éxito", "El mensaje esperado no está presente en la respuesta.")


if __name__ == "__main__":
    asyncio.run(unittest.main())
