import unittest
from datetime import datetime
from gestion_de_citas import Cita, Tratamiento, GestionCitas  # Asegúrate de que el archivo principal se llama `gestion_de_citas.py`

class TestGestionCitas(unittest.TestCase):
    def setUp(self):
        # Configuración inicial para cada prueba
        self.gestion = GestionCitas()
        
        # Crear tratamientos y citas de ejemplo
        self.tratamiento1 = Tratamiento("Vacunación", "Vacunación general", 30.0)
        self.tratamiento2 = Tratamiento("Limpieza dental", "Limpieza bucal", 50.0)
        
        # Crear fechas para las citas
        self.fecha1 = datetime(2024, 11, 5, 10, 0)
        self.fecha2 = datetime(2024, 11, 5, 15, 0)
        
        # Crear citas
        self.cita1 = Cita("Rex", "Juan Perez", self.tratamiento1, self.fecha1)
        self.cita2 = Cita("Bella", "Ana Gomez", self.tratamiento2, self.fecha2)

    def test_registrar_cita(self):
        # Prueba para registrar una cita
        self.gestion.registrar_cita(self.cita1)
        self.assertIn(self.cita1, self.gestion.citas)
        
        # Intentar registrar una cita duplicada debería lanzar un error
        with self.assertRaises(ValueError):
            self.gestion.registrar_cita(self.cita1)

    def test_modificar_cita(self):
        # Registrar la cita y modificar su tratamiento y fecha
        self.gestion.registrar_cita(self.cita1)
        nuevo_tratamiento = Tratamiento("Desparasitación", "Desparasitación interna", 25.0)
        nueva_fecha = datetime(2024, 11, 6, 10, 30)
        
        # Modificar la cita
        self.gestion.modificar_cita(self.cita1, nuevo_tratamiento, nueva_fecha)
        
        # Comprobar los cambios
        self.assertEqual(self.cita1.tratamiento, nuevo_tratamiento)
        self.assertEqual(self.cita1.fecha_hora, nueva_fecha)

    def test_cancelar_cita(self):
        # Registrar y cancelar una cita
        self.gestion.registrar_cita(self.cita1)
        self.gestion.cancelar_cita(self.cita1)
        
        # Comprobar que la cita fue removida
        self.assertNotIn(self.cita1, self.gestion.citas)

    def test_finalizar_cita(self):
        # Registrar la cita y finalizarla con un método de pago
        self.gestion.registrar_cita(self.cita1)
        self.gestion.finalizar_cita(self.cita1, [self.tratamiento1], "efectivo")
        
        # Verificar que la cita esté marcada como realizada y que la factura tenga el método de pago
        self.assertTrue(self.cita1.realizado)
        self.assertEqual(self.cita1.factura.metodo_pago, "efectivo")
        
        # Intentar finalizar una cita ya realizada no debe cambiar el estado
        with self.assertRaises(ValueError):
            self.gestion.finalizar_cita(self.cita1, [self.tratamiento1], "efectivo")

    def test_ver_todas_las_citas(self):
        # Registrar múltiples citas y verificar la cantidad total
        self.gestion.registrar_cita(self.cita1)
        self.gestion.registrar_cita(self.cita2)
        
        # Comprobar que ambas citas están en la lista
        todas_citas = self.gestion.citas
        self.assertEqual(len(todas_citas), 2)
        self.assertIn(self.cita1, todas_citas)
        self.assertIn(self.cita2, todas_citas)

if __name__ == "__main__":
    unittest.main()
