import os
import tempfile
import json
import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from clinica.models.tabla_citas import Cita
from clinica.services.gestion_de_citas import GestionCitas
from datetime import datetime


class TestGestionCitas(unittest.TestCase):

    def setUp(self):
        # Crear un mock de la sesión de la base de datos
        self.db_session = MagicMock(spec=Session)
        self.gestion_citas = GestionCitas(db_session=self.db_session)

    def test_exportar_citas_a_json_exitoso(self):
        # Configurar una cita simulada
        cita_mock = Cita(
            id_cita=1,
            fecha=datetime(2024, 11, 10, 10, 0),
            descripcion="Consulta general",
            metodo_pago="Tarjeta",
            estado="Finalizada",
            id_mascota=1,
            id_cliente=1,
            id_tratamiento=1,
        )
        cita_mock.to_dict = MagicMock(return_value={
            "id_cita": 1,
            "fecha": "2024-11-10T10:00:00",
            "descripcion": "Consulta general",
            "metodo_pago": "Tarjeta",
            "estado": "Finalizada",
            "id_mascota": 1,
            "id_cliente": 1,
            "id_tratamiento": 1,
        })
        self.db_session.query().all.return_value = [cita_mock]

        # Crear un archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            temp_file_path = temp_file.name

        # Llamar a la función
        resultado = self.gestion_citas.exportar_citas_a_json(temp_file_path)

        # Verificar que el archivo contiene datos
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            self.assertTrue(content, "El archivo JSON está vacío.")
            datos = json.loads(content)
            self.assertTrue(any(cita['id_cita'] == 1 for cita in datos))

        # Verificar mensaje de éxito
        self.assertIn("Citas exportadas a", resultado)

        # Eliminar el archivo temporal
        os.remove(temp_file_path)

    def test_registrar_cita_exito(self):
        cita_data = {
            'fecha': datetime(2024, 11, 10, 10, 0),
            'descripcion': 'Consulta general',
            'id_mascota': 1,
            'id_cliente': 1,
            'id_tratamiento': 1,
            'metodo_pago': "Tarjeta",
            'estado': "Pendiente"
        }

        # Simular que no existe cita duplicada
        self.db_session.query().filter_by().first.return_value = None

        # Llamar a la función
        resultado = self.gestion_citas.registrar_cita(cita_data)

        # Verificar que la cita se añadió y se realizó commit
        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()
        self.assertIsInstance(resultado, Cita)

    def test_registrar_cita_duplicada(self):
        cita_data = {
            'fecha': datetime(2024, 11, 10, 10, 0),
            'descripcion': 'Consulta general',
            'id_mascota': 1,
            'id_cliente': 1,
            'id_tratamiento': 1,
            'metodo_pago': "Tarjeta",
            'estado': "Pendiente"
        }

        # Simular cita duplicada
        self.db_session.query().filter_by().first.return_value = Cita(
            id_cita=1, fecha='2024-11-10 10:00:00', descripcion='Consulta general', id_mascota=1, id_cliente=1
        )

        # Llamar a la función
        with self.assertRaises(ValueError) as context:
            self.gestion_citas.registrar_cita(cita_data)

        self.assertEqual(str(context.exception), "Ya existe una cita para este animal, dueño y horario.")
        self.db_session.add.assert_not_called()
        self.db_session.commit.assert_not_called()

    def test_registrar_cita_integrity_error(self):
        # Simular un IntegrityError al intentar añadir la cita
        self.db_session.add.side_effect = IntegrityError("Error de integridad", None, None)

        # Incluir todos los campos requeridos
        cita_data = {
            'fecha': datetime(2024, 11, 10, 10, 0),
            'descripcion': 'Consulta general',
            'id_mascota': 1,
            'id_cliente': 1,
            'id_tratamiento': 1,
            'estado': 'Pendiente'  # Asegúrate de incluir este campo
        }

        # Ejecutar el método con validación desactivada
        with self.assertRaises(ValueError) as context:
            self.gestion_citas.registrar_cita(cita_data, validar_duplicados=False)

        # Verificar que el mensaje de error es el esperado
        self.assertEqual(str(context.exception), "Error: No se pudo registrar la cita debido a un problema de integridad.")

        # Verificar que rollback fue llamado
        self.db_session.rollback.assert_called_once()


    def test_registrar_cita_falta_campo_obligatorio(self):
        cita_data = {
            'fecha': datetime(2024, 11, 10, 10, 0),
            'descripcion': 'Consulta general',
            'id_mascota': 1,
            'id_cliente': 1,
            'id_tratamiento': 1,
            # Falta el campo 'estado'
        }

        with self.assertRaises(ValueError) as context:
            self.gestion_citas.registrar_cita(cita_data)

        self.assertEqual(str(context.exception), "El campo 'estado' es obligatorio para registrar una cita.")

    def test_finalizar_cita_exito(self):
        # Crear un mock de la cita
        cita_mock = Cita(
            id_cita=1,
            fecha=datetime(2024, 11, 10, 10, 0),
            descripcion="Consulta general",
            metodo_pago=None,
            estado="Pendiente",
            id_mascota=1,
            id_cliente=1,
            id_tratamiento=1,
        )
        self.db_session.query().filter_by().first.return_value = cita_mock

        metodo_pago = "Tarjeta"

        # Llamar al método
        resultado = self.gestion_citas.finalizar_cita(1, metodo_pago)

        # Verificar los cambios en los campos
        self.assertEqual(cita_mock.metodo_pago, metodo_pago)  # Validar el método de pago
        self.assertEqual(cita_mock.estado, "Finalizada")  # Validar el estado
        self.db_session.commit.assert_called_once()  # Verificar que se hizo commit
        self.assertEqual(resultado, cita_mock)  # Validar que el resultado es la cita actualizada


    def test_finalizar_cita_metodo_pago_invalido(self):
        """
        Verifica que se lance un ValueError cuando se pasa un método de pago inválido.
        """
        with self.assertRaises(ValueError) as context:
            self.gestion_citas.finalizar_cita(1, "Cheque")  # Solo dos argumentos: id_cita y metodo_pago

        # Verificar que el mensaje de excepción es correcto
        self.assertEqual(
            str(context.exception),
            "Método de pago 'Cheque' no es válido. Métodos aceptados: Efectivo, Tarjeta, Bizum, Transferencia."
        )

        # Verificar que no se intentó realizar un commit
        self.db_session.commit.assert_not_called()

    def test_cancelar_cita_exito(self):
        cita_mock = Cita(
            id_cita=1,
            fecha=datetime(2024, 11, 10, 10, 0),
            descripcion="Consulta general",
            estado="Pendiente",
            id_mascota=1,
            id_cliente=1,
            id_tratamiento=1,
        )
        self.db_session.query().filter_by().first.return_value = cita_mock

        resultado = self.gestion_citas.cancelar_cita(1)

        # Verificar cambios
        self.assertEqual(cita_mock.estado, "Cancelada")
        self.db_session.commit.assert_called_once()
        self.assertEqual(resultado, cita_mock)

    def test_cancelar_cita_no_encontrada(self):
        self.db_session.query().filter_by().first.return_value = None

        resultado = self.gestion_citas.cancelar_cita(1)

        self.assertIsNone(resultado)
        self.db_session.commit.assert_not_called()

    def test_cancelar_cita_sqlalchemy_error(self):
        self.db_session.commit.side_effect = SQLAlchemyError("Error al ejecutar el commit.")

        cita_mock = Cita(id_cita=1, estado="Pendiente")
        self.db_session.query().filter_by().first.return_value = cita_mock

        with self.assertRaises(RuntimeError) as context:
            self.gestion_citas.cancelar_cita(1)

        self.assertIn("Error al cancelar la cita", str(context.exception))
        self.db_session.rollback.assert_called_once()

    def test_ver_todas_las_citas_filtradas_por_estado(self):
        # Crear un mock de una cita con todos los atributos necesarios
        cita_mock = MagicMock()
        cita_mock.to_dict.return_value = {
            "id_cita": 1,
            "fecha": "2024-12-01T10:00:00",
            "descripcion": "Consulta general",
            "metodo_pago": "Tarjeta",
            "estado": "Finalizada",
            "id_mascota": 5,
            "id_cliente": 3,
            "id_tratamiento": 2,
        }

        # Configurar el mock de la consulta
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query  # Configurar filter() para devolver el mismo mock
        mock_query.all.return_value = [cita_mock]  # Configurar all() para devolver una lista con la cita
        mock_query.count.return_value = 1  # Configurar count() para devolver 1

        # Configurar el mock de la sesión de base de datos
        self.db_session.query.return_value = mock_query

        # Llamar al método con estado="Finalizada"
        resultado = self.gestion_citas.ver_todas_las_citas(estado="Finalizada")

        # Depuración
        print("Resultado final:", resultado)
        print("Llamadas al mock de sesión:", self.db_session.mock_calls)
        print("Llamadas al mock de consulta:", mock_query.mock_calls)

        # Verificar el resultado
        self.assertEqual(resultado["total"], 1)  # Asegurar que el total es correcto
        self.assertEqual(len(resultado["citas"]), 1)  # Asegurar que se devuelve una cita
        self.assertEqual(resultado["citas"][0]["estado"], "Finalizada")  # Verificar el estado de la cita

    def test_ver_todas_las_citas_con_registros(self):
        # Crear mocks de citas con datos simulados
        cita_mock_1 = MagicMock()
        cita_mock_1.to_dict.return_value = {
            "id_cita": 1,
            "fecha": "2024-11-10T10:00:00",
            "descripcion": "Consulta general"
        }
        cita_mock_2 = MagicMock()
        cita_mock_2.to_dict.return_value = {
            "id_cita": 2,
            "fecha": "2024-11-11T10:00:00",
            "descripcion": "Chequeo dental"
        }

        # Configurar el mock de la consulta
        mock_query = MagicMock()
        mock_query.all.return_value = [cita_mock_1, cita_mock_2]  # Resultado de .all()
        mock_query.count.return_value = 2  # Resultado de .count()
        self.db_session.query.return_value = mock_query

        # Llamar al método
        resultado = self.gestion_citas.ver_todas_las_citas()

        # Depuración
        print("Resultado devuelto:", resultado)
        print("Llamadas al mock de consulta:", mock_query.mock_calls)

        # Verificar el resultado
        self.assertEqual(resultado["total"], 2)  # Total de citas
        self.assertEqual(len(resultado["citas"]), 2)  # Número de citas en la lista
        self.assertEqual(resultado["citas"][0]["id_cita"], 1)  # Verificar ID de la primera cita
        self.assertEqual(resultado["citas"][1]["descripcion"], "Chequeo dental")  # Verificar descripción de la segunda cita



if __name__ == '__main__':
    unittest.main()