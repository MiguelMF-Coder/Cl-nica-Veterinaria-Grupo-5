import unittest
import streamlit as st
from unittest.mock import patch, MagicMock
from streamlit.pages.Tratamientos_pag import (
    validar_tratamiento, show_new_treatment, show_tratamientos_list,
    show_edit_form, delete_treatment
)

class TestTratamientos(unittest.TestCase):
    def setUp(self):
        self.tratamiento_test = {
            "id_tratamiento": 1,
            "nombre_tratamiento": "Vacunación",
            "descripcion": "Vacuna anual",
            "precio": 50.0,
            "estado": "Activo",
            "id_cliente": 1
        }

    def test_validar_tratamiento(self):
        # Test válido
        self.assertTrue(validar_tratamiento(
            "Vacunación", "Descripción", 50.0, "Activo", 1
        )[0])

        # Test precio negativo
        self.assertFalse(validar_tratamiento(
            "Vacunación", "Descripción", -10.0, "Activo", 1
        )[0])

        # Test nombre largo
        self.assertFalse(validar_tratamiento(
            "x" * 101, "Descripción", 50.0, "Activo", 1
        )[0])

        # Test estado inválido
        self.assertFalse(validar_tratamiento(
            "Vacunación", "Descripción", 50.0, "Estado Inválido", 1
        )[0])

    @patch('streamlit.form')
    @patch('streamlit.text_input')
    @patch('streamlit.text_area')
    @patch('streamlit.number_input')
    @patch('streamlit.selectbox')
    @patch('requests.post')
    def test_nuevo_tratamiento(self, mock_post, mock_select, mock_number, 
                             mock_area, mock_text, mock_form):
        # Configurar mocks
        mock_form.return_value.__enter__.return_value = None
        mock_text.return_value = "Nuevo Tratamiento"
        mock_area.return_value = "Descripción test"
        mock_number.return_value = 100.0
        mock_select.return_value = "Activo"
        mock_post.return_value.status_code = 201

        with patch('streamlit.success') as mock_success:
            show_new_treatment()
            mock_success.assert_not_called()

    @patch('requests.get')
    def test_listar_tratamientos(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [self.tratamiento_test]

        with patch('streamlit.container'):
            show_tratamientos_list()

    @patch('streamlit.form')
    @patch('requests.put')
    def test_editar_tratamiento(self, mock_put, mock_form):
        mock_form.return_value.__enter__.return_value = None
        mock_put.return_value.status_code = 200

        with patch('streamlit.success') as mock_success:
            show_edit_form(self.tratamiento_test)
            mock_success.assert_not_called()

    @patch('requests.delete')
    def test_eliminar_tratamiento(self, mock_delete):
        mock_delete.return_value.status_code = 200
        
        with patch('streamlit.success') as mock_success:
            delete_treatment(1)
            mock_success.assert_called_once()

    @patch('requests.get')
    def test_filtros_tratamiento(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [self.tratamiento_test]

        with patch('streamlit.container'):
            with patch('streamlit.text_input') as mock_input:
                mock_input.return_value = "Vacunación"
                show_tratamientos_list()

if __name__ == '__main__':
    unittest.main()