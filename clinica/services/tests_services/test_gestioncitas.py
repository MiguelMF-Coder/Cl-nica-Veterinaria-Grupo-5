# test_gestioncitas.py

import sys
import os
import json
import tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Verificar si la ruta se ha añadido correctamente
print("Rutas en sys.path:")
for path in sys.path:
    print(path)

import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from clinica.models.tabla_citas import Cita
from clinica.services.gestion_de_citas import GestionCitas
from clinica.dbconfig import Base  
from datetime import datetime

class TestGestionCitas(unittest.TestCase):

    def setUp(self):
        # Crear un mock de la sesión de la base de datos
        self.db_session = MagicMock(spec=Session)
        self.gestion_citas = GestionCitas(db_session=self.db_session)        

    def test_exportar_citas_a_json_exitoso(self):
            # Configurar una cita de ejemplo y simular su presencia en la base de datos
            cita_mock = Cita(id_cita=1, fecha="2024-11-10 10:00:00", descripcion="Consulta general", id_mascota=1, id_cliente=1)
            cita_mock.to_dict = MagicMock(return_value={
                "id_cita": 1,
                "fecha": "2024-11-10 10:00:00",
                "descripcion": "Consulta general",
                "id_mascota": 1,
                "id_cliente": 1
            })
            self.db_session.query().all.return_value = [cita_mock]

            # Crear un archivo temporal para exportar los datos
            with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
                temp_file_path = temp_file.name

            # Llamar a la función de exportación
            resultado = self.gestion_citas.exportar_citas_a_json(temp_file_path)

            # Leer el archivo y verificar que contiene datos
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                self.assertTrue(content, "El archivo JSON está vacío.")  # Verifica que el archivo no esté vacío

                datos = json.loads(content)
                print("Datos exportados:", datos)  # Depuración: Imprimir datos exportados
                self.assertTrue(any(cita['id_cita'] == 1 for cita in datos))

            # Verificar mensaje de éxito
            self.assertIn("Citas exportadas a", resultado)
            
            # Limpieza del archivo de prueba
            os.remove(temp_file_path)

    def test_registrar_cita_exito(self):
        # Datos de prueba con campos válidos
        id_tratamiento = {
        'fecha': datetime.strptime('2024-11-10 10:00:00', '%Y-%m-%d %H:%M:%S'),
        'descripcion': 'Consulta general',
        'id_mascota': 1,
        'id_cliente': 1,
        'id_tratamiento': 1
        }

        # Simular que la cita no existe en la base de datos
        self.db_session.query().filter_by().first.return_value = None

        # Llamar a la función de prueba
        resultado = self.gestion_citas.registrar_cita(id_tratamiento)

        # Verificar que la cita fue añadida y se hizo commit
        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()
        resultado = self.gestion_citas.registrar_cita(id_tratamiento)
        print("Resultado de la función:", resultado)
        self.assertIn("Cita registrada con éxito para el cliente ID", resultado)


    def test_registrar_cita_duplicada(self):
        # Datos de prueba con campos válidos
        id_tratamiento = {
            'fecha': '2024-11-10 10:00:00',
            'descripcion': 'Consulta general',
            'id_mascota': 1,
            'id_cliente': 1,
            'id_tratamiento': 1
        }

        # Simular que la cita ya existe en la base de datos
        self.db_session.query().filter_by().first.return_value = Cita(
            id_cita=1, fecha='2024-11-10 10:00:00', descripcion='Consulta general', id_mascota=1, id_cliente=1
        )

        # Llamar a la función de prueba y verificar que se lanzó un error de duplicación
        with self.assertRaises(ValueError) as context:
            self.gestion_citas.registrar_cita(id_tratamiento)

        self.assertEqual(str(context.exception), "Ya existe una cita para este animal, dueño y horario.")
        self.db_session.add.assert_not_called()
        self.db_session.commit.assert_not_called()

    def test_buscar_cita_exito(self):
        # Configurar la sesión para devolver una cita simulada con campos válidos
        cita_mock = Cita(
            id_cita=1, fecha='2024-11-10 10:00:00', descripcion='Consulta general', id_mascota=1, id_cliente=1
        )
        self.db_session.query().filter_by().first.return_value = cita_mock

        # Llamar a la función de prueba
        resultado = self.gestion_citas.buscar_cita('Fido', 'Juan')

        # Verificar que la función devuelve la cita esperada
        self.assertEqual(resultado, cita_mock)

    def test_buscar_cita_no_encontrada(self):
        # Configurar la sesión para devolver None (cita no encontrada)
        self.db_session.query().filter_by().first.return_value = None

        # Llamar a la función de prueba
        resultado = self.gestion_citas.buscar_cita('Fido', 'Juan')

        # Verificar que la función devuelve None y muestra el mensaje de cita no encontrada
        self.assertIsNone(resultado)

    def test_cancelar_cita_exito(self):
        # Configurar la sesión para devolver una cita simulada con campos válidos
        cita_mock = Cita(
            id_cita=1, fecha='2024-11-10 10:00:00', descripcion='Consulta general', id_mascota=1, id_cliente=1
        )
        self.db_session.query().filter_by().first.return_value = cita_mock

        # Llamar a la función de prueba
        resultado = self.gestion_citas.cancelar_cita(1)

        # Verificar que la cita fue eliminada y se hizo commit
        self.db_session.delete.assert_called_once_with(cita_mock)
        self.db_session.commit.assert_called_once()
        self.assertIn("Cita con ID '1' cancelada con éxito.", resultado)

    def test_cancelar_cita_no_encontrada(self):
        # Configurar la sesión para devolver None (cita no encontrada)
        self.db_session.query().filter_by().first.return_value = None

        # Llamar a la función de prueba
        resultado = self.gestion_citas.cancelar_cita(1)

        # Verificar que se muestra el mensaje de cita no encontrada y no se elimina nada
        self.assertIn("Error: No se encontró la cita con ID '1'.", resultado)
        self.db_session.delete.assert_not_called()
        self.db_session.commit.assert_not_called()

if __name__ == '__main__':
    unittest.main()
# test_gestioncitas.py
