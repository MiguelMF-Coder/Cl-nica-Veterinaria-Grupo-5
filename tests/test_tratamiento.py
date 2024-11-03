import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from clinica.models.tabla_tratamiento import tratamientos
from clinica.services.tratamiento import GestionTratamientos

class TestGestionTratamientos(unittest.TestCase):

    def setUp(self):
        # Crear un mock de la sesión de la base de datos
        self.db_session = MagicMock(spec=Session)
        self.gestion_tratamientos = GestionTratamientos(db_session=self.db_session)

    def test_dar_alta_tratamiento_exito(self):
        # Datos de prueba
        tratamiento_data = {
            'nombre_tratamiento': 'Vacunación',
            'descripcion': 'Vacunación general',
            'precio': 50
        }

        # Simular que el tratamiento no existe en la base de datos
        self.db_session.query().filter_by().first.return_value = None

        # Llamar a la función de prueba
        resultado = self.gestion_tratamientos.dar_alta_tratamiento(tratamiento_data)

        # Verificar que el tratamiento fue añadido y se hizo commit
        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()
        self.assertIn("dado de alta con éxito", resultado)

    def test_dar_alta_tratamiento_duplicado(self):
        # Datos de prueba
        tratamiento_data = {
            'nombre_tratamiento': 'Vacunación',
            'descripcion': 'Vacunación general',
            'precio': 50
        }

        # Simular que el tratamiento ya existe en la base de datos
        self.db_session.query().filter_by().first.return_value = tratamientos()

        # Llamar a la función de prueba y verificar el resultado
        resultado = self.gestion_tratamientos.dar_alta_tratamiento(tratamiento_data)

        self.assertIn("ya está registrado", resultado)
        self.db_session.add.assert_not_called()
        self.db_session.commit.assert_not_called()

    def test_dar_baja_tratamiento_exito(self):
        # Simular que el tratamiento existe en la base de datos
        tratamiento_mock = tratamientos(nombre_tratamiento='Vacunación')
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
        self.assertIn("no se encontró", resultado)
        self.db_session.delete.assert_not_called()
        self.db_session.commit.assert_not_called()

    def test_modificar_tratamiento_exito(self):
        # Simular que el tratamiento existe en la base de datos
        tratamiento_mock = tratamientos(id_tratamiento=1, nombre_tratamiento='Vacunación')
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
        self.assertIn("no se encontró", resultado)
        self.db_session.commit.assert_not_called()

if __name__ == '__main__':
    unittest.main()
