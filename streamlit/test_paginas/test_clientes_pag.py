import unittest
import streamlit as st
from unittest.mock import patch, MagicMock
from streamlit.pages.Clientes_pag import (
    validar_dni, validar_telefono, show_nuevo_cliente, show_lista_clientes,
    show_edit_form, show_add_mascota_form, delete_cliente, mostrar_mascotas
)

class TestClientesPage(unittest.TestCase):
    def setUp(self):
        self.session_state = {}
        self.mock_requests = MagicMock()

    def test_validar_dni(self):
        self.assertTrue(validar_dni("12345678A")[0])
        self.assertFalse(validar_dni("1234567A")[0])
        self.assertFalse(validar_dni("12345678")[0])
        self.assertFalse(validar_dni("ABCDEFGHI")[0])

    def test_validar_telefono(self):
        self.assertTrue(validar_telefono("600123456")[0])
        self.assertTrue(validar_telefono("722123456")[0])
        self.assertTrue(validar_telefono("911123456")[0])
        self.assertFalse(validar_telefono("500123456")[0])
        self.assertFalse(validar_telefono("60012345")[0])
        self.assertFalse(validar_telefono("60012345A")[0])

    @patch('streamlit.form')
    @patch('streamlit.text_input')
    @patch('streamlit.number_input')
    @patch('requests.post')
    def test_nuevo_cliente_form(self, mock_post, mock_number, mock_text, mock_form):
        mock_form.return_value.__enter__.return_value = None
        mock_text.side_effect = ["Juan Pérez", "12345678A", "Calle Test", "600123456"]
        mock_number.return_value = 30
        mock_post.return_value.status_code = 201

        with patch('streamlit.success') as mock_success:
            show_nuevo_cliente()
            mock_success.assert_called_once()

    @patch('requests.get')
    def test_lista_clientes_filtros(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {
                "id_cliente": 1,
                "nombre_cliente": "Juan Pérez",
                "dni": "12345678A",
                "telefono": "600123456",
                "direccion": "Calle Test",
                "edad": 30
            }
        ]

        with patch('streamlit.container'):
            show_lista_clientes()

    @patch('streamlit.form')
    @patch('requests.put')
    def test_editar_cliente(self, mock_put, mock_form):
        cliente = {
            "id_cliente": 1,
            "nombre_cliente": "Juan Pérez",
            "dni": "12345678A",
            "telefono": "600123456",
            "direccion": "Calle Test",
            "edad": 30
        }
        
        mock_form.return_value.__enter__.return_value = None
        mock_put.return_value.status_code = 200

        with patch('streamlit.success') as mock_success:
            show_edit_form(cliente)
            mock_success.assert_called_once()

    @patch('requests.get')
    def test_mostrar_mascotas(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {
                "id_mascota": 1,
                "nombre_mascota": "Firulais",
                "raza": "Labrador",
                "edad": 3,
                "estado": "Vivo"
            }
        ]

        with patch('streamlit.container'):
            mostrar_mascotas(1)

    @patch('requests.delete')
    def test_eliminar_cliente(self, mock_delete):
        mock_delete.return_value.status_code = 200
        
        with patch('streamlit.success') as mock_success:
            delete_cliente(1)
            mock_success.assert_called_once()

    @patch('streamlit.form')
    @patch('requests.post')
    def test_add_mascota_form(self, mock_post, mock_form):
        mock_form.return_value.__enter__.return_value = None
        mock_post.return_value.status_code = 201

        with patch('streamlit.success') as mock_success:
            show_add_mascota_form(1)
            mock_success.assert_called_once()

    def test_session_state_initialization(self):
        with patch('streamlit.session_state', self.session_state):
            show_lista_clientes()
            self.assertIn('mostrar_mascotas', self.session_state)
            self.assertIn('confirmar_eliminacion', self.session_state)
            self.assertIn('cliente_a_eliminar', self.session_state)

if __name__ == '__main__':
    unittest.main()