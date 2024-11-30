# test_tratamiento.py

import sys
import os
import tempfile
import json

# Añadir la ruta de la carpeta raíz del proyecto al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from clinica.models import Tratamiento, Cita, Cliente, Mascota
from clinica.services.gestion_tratamiento import GestionTratamientos


class TestGestionTratamientos(unittest.TestCase):

    def setUp(self):
        # Crear un mock de la sesión de la base de datos
        self.db_session = MagicMock(spec=Session)
        self.gestion_tratamientos = GestionTratamientos(db_session=self.db_session)


    def test_exportar_tratamientos_a_json_exitoso(self):
        # Crear un tratamiento simulado y configurar el mock
        tratamiento_mock = Tratamiento(id_tratamiento=1, nombre_tratamiento="Vacunación", descripcion="Vacunación general", precio=50)
        tratamiento_mock.to_dict = MagicMock(return_value={
            "id_tratamiento": 1,
            "nombre_tratamiento": "Vacunación",
            "descripcion": "Vacunación general",
            "precio": 50
        })
        self.db_session.query().all.return_value = [tratamiento_mock]

        # Usar un archivo temporal para la exportación
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            temp_file_path = temp_file.name

        # Ejecutar la función de exportación
        resultado = self.gestion_tratamientos.exportar_tratamientos_a_json(temp_file_path)

        # Verificar que el archivo no esté vacío
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            self.assertTrue(content, "El archivo JSON está vacío.")

            datos = json.loads(content)
            self.assertTrue(any(tratamiento['id_tratamiento'] == 1 for tratamiento in datos))

        # Verificar mensaje de éxito
        self.assertIn("Tratamientos exportados a", resultado)
        
        # Limpieza del archivo de prueba
        os.remove(temp_file_path)

    def test_dar_alta_tratamiento_exito(self):
        # Datos de prueba
        tratamiento_data = {
            'nombre_tratamiento': 'Vacunación',
            'descripcion': 'Vacunación general',
            'precio': 50,
            'estado': 'Activo',  # Añadir 'estado' si es obligatorio
            'id_cliente': 1
        }

        # Simular que el tratamiento no existe en la base de datos
        self.db_session.query().filter_by().first.return_value = None

        # Llamar a la función de prueba
        resultado = self.gestion_tratamientos.dar_alta_tratamiento(tratamiento_data)

        # Verificar que el tratamiento fue añadido y se hizo commit
        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()

        # Comprobar que el resultado sea un objeto de tipo Tratamiento y verificar atributos
        self.assertIsInstance(resultado, Tratamiento)
        self.assertEqual(resultado.nombre_tratamiento, tratamiento_data['nombre_tratamiento'])
        self.assertEqual(resultado.descripcion, tratamiento_data['descripcion'])
        self.assertEqual(resultado.precio, tratamiento_data['precio'])
        self.assertEqual(resultado.id_cliente, tratamiento_data['id_cliente'])


    def test_dar_alta_tratamiento_duplicado(self):
        # Datos de prueba
        tratamiento_data = {
            'nombre_tratamiento': 'Vacunación',
            'descripcion': 'Vacunación general',
            'precio': 50,
            'id_cliente': 1
        }

        # Simular que el tratamiento ya existe en la base de datos
        self.db_session.query().filter_by().first.return_value = Tratamiento()

        # Llamar a la función de prueba y verificar el resultado
        resultado = self.gestion_tratamientos.dar_alta_tratamiento(tratamiento_data)

        self.assertIn("ya está registrado", resultado)
        self.db_session.add.assert_not_called()
        self.db_session.commit.assert_not_called()

    def test_dar_baja_tratamiento_exito(self):
        # Simular que el tratamiento existe en la base de datos
        tratamiento_mock = Tratamiento(nombre_tratamiento='Vacunación')
        self.db_session.query().filter_by().first.return_value = tratamiento_mock

        # Llamar a la función de prueba
        resultado = self.gestion_tratamientos.dar_baja_tratamiento('Vacunación')

        # Verificar que el tratamiento fue eliminado y se hizo commit
        self.db_session.delete.assert_called_once_with(tratamiento_mock)
        self.db_session.commit.assert_called_once()
        self.assertIn("dado de baja con éxito", resultado)

    def test_dar_baja_tratamiento_no_encontrado(self):
        # Simular que el tratamiento no existe en la base de datos
        self.db_session.query().filter_by().first.return_value = None

        # Llamar a la función de prueba
        resultado = self.gestion_tratamientos.dar_baja_tratamiento('Vacunación')

        # Verificar el resultado y que no se intentó eliminar nada
        self.assertIn("Error: No se encontró el tratamiento 'Vacunación'.", resultado)
        self.db_session.delete.assert_not_called()
        self.db_session.commit.assert_not_called()

    def test_modificar_tratamiento_exito(self):
        # Simular que el tratamiento existe en la base de datos
        tratamiento_mock = Tratamiento(id_tratamiento=1, nombre_tratamiento='Vacunación')
        self.db_session.query().filter_by().first.return_value = tratamiento_mock

        # Datos de modificación
        nuevos_datos = {'descripcion': 'Vacunación avanzada', 'precio': 60}

        # Llamar a la función de prueba
        resultado = self.gestion_tratamientos.modificar_tratamiento(1, nuevos_datos)

        # Verificar que los atributos fueron modificados y se hizo commit
        self.db_session.commit.assert_called_once()
        self.assertIn("modificado con éxito", resultado)

    def test_modificar_tratamiento_no_encontrado(self):
        # Simular que el tratamiento no existe en la base de datos
        self.db_session.query().filter_by().first.return_value = None

        # Llamar a la función de prueba
        resultado = self.gestion_tratamientos.modificar_tratamiento(1, {'descripcion': 'Vacunación avanzada'})

        # Verificar el resultado y que no se hizo commit
        self.assertIn("Error: No se encontró el tratamiento con ID '1'.", resultado)
        self.db_session.commit.assert_not_called()

    def test_obtener_datos_factura_exitoso(self):
        # Mockea los datos para tratamiento, cita, cliente y mascota
        tratamiento = Tratamiento(id_tratamiento=1, nombre_tratamiento="Vacunación", estado="Finalizada")
        cita = Cita(id_cita=1, id_tratamiento=1, id_cliente=1, id_mascota=1, descripcion="Cita de vacunación")
        cliente = Cliente(id_cliente=1, nombre_cliente="Juan Perez", dni="12345678A")
        mascota = Mascota(id_mascota=1, nombre_mascota="Fido", raza="Labrador")

        # Configura los mocks
        self.db_session.query().filter_by().first.side_effect = [tratamiento, cita, cliente, mascota]

        # Llama a la función
        resultado = self.gestion_tratamientos.obtener_datos_factura(id_tratamiento=1)

        # Verifica que el resultado contiene todos los datos necesarios
        self.assertEqual(resultado["cliente"], cliente)
        self.assertEqual(resultado["mascota"], mascota)
        self.assertEqual(resultado["cita"], cita)
        self.assertEqual(resultado["tratamiento"], tratamiento)

    def test_obtener_datos_factura_tratamiento_no_encontrado(self):
        # Simula que no se encuentra el tratamiento
        self.db_session.query().filter_by().first.return_value = None

        # Llama a la función
        resultado = self.gestion_tratamientos.obtener_datos_factura(id_tratamiento=1)

        # Verifica que se devuelve el error correspondiente
        self.assertEqual(resultado, {"error": "Tratamiento no encontrado"})

    def test_obtener_datos_factura_cita_no_encontrada(self):
        # Mockea el tratamiento, pero la cita no se encuentra
        tratamiento = Tratamiento(id_tratamiento=1, nombre_tratamiento="Vacunación")
        self.db_session.query().filter_by().first.side_effect = [tratamiento, None]

        # Llama a la función
        resultado = self.gestion_tratamientos.obtener_datos_factura(id_tratamiento=1)

        # Verifica que se devuelve el error correspondiente
        self.assertEqual(resultado, {"error": "Cita no encontrada para el tratamiento especificado"})

    def test_obtener_datos_factura_cliente_o_mascota_no_encontrados(self):
        # Mockea el tratamiento y la cita, pero no el cliente o la mascota
        tratamiento = Tratamiento(id_tratamiento=1, nombre_tratamiento="Vacunación")
        cita = Cita(id_cita=1, id_tratamiento=1, id_cliente=1, id_mascota=1)
        self.db_session.query().filter_by().first.side_effect = [tratamiento, cita, None, None]

        # Llama a la función
        resultado = self.gestion_tratamientos.obtener_datos_factura(id_tratamiento=1)

        # Verifica que se devuelve el error correspondiente
        self.assertEqual(resultado, {"error": "Cliente o mascota no encontrados"})

    def test_validar_tratamiento_Finalizada_true(self):
        # Crea un tratamiento marcado como Finalizada
        tratamiento = Tratamiento(id_tratamiento=1, nombre_tratamiento="Vacunación", estado="Finalizada")
        resultado = self.gestion_tratamientos.validar_tratamiento_Finalizada(tratamiento)
        self.assertTrue(resultado)

    def test_validar_tratamiento_Finalizada_false(self):
        # Crea un tratamiento no Finalizada
        tratamiento = Tratamiento(id_tratamiento=1, nombre_tratamiento="Vacunación", estado="Pendiente")
        resultado = self.gestion_tratamientos.validar_tratamiento_Finalizada(tratamiento)
        self.assertFalse(resultado)

    def test_validar_tratamiento_Finalizada_sin_estado(self):
        # Crea un tratamiento sin el atributo `estado`
        tratamiento = Tratamiento(id_tratamiento=1, nombre_tratamiento="Vacunación")
        tratamiento.estado = None  # Asigna None en lugar de eliminar el atributo

        resultado = self.gestion_tratamientos.validar_tratamiento_Finalizada(tratamiento)
        self.assertEqual(resultado, {"error": "El modelo Tratamiento no tiene el atributo 'estado'"})

if __name__ == '__main__':
    unittest.main()
