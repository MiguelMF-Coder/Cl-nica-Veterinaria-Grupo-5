import unittest
from tratamiento import Tratamiento, GestionTratamientos

class TestGestionTratamientos(unittest.TestCase):
    def setUp(self):
        # Configura un entorno de prueba con una instancia de GestionTratamientos
        self.gestion = GestionTratamientos()
        
        # Crear varios tratamientos
        self.tratamiento_analisis = Tratamiento("Análisis", "Análisis de sangre, orina, etc.", 50)
        self.tratamiento_vacunacion = Tratamiento("Vacunación", "Vacunación general", 30)
        self.tratamiento_desparasitacion = Tratamiento("Desparasitación", "Desparasitación interna y externa", 25)
        self.tratamiento_ecografia = Tratamiento("Ecografías", "Ecografía abdominal y torácica", 100)
        self.tratamiento_limpieza = Tratamiento("Limpieza dental", "Limpieza dental para evitar enfermedades bucales", 75)
        self.tratamiento_cirugia = Tratamiento("Cirugía básica - Castración", "Castración de perros y gatos", 200)
        
        # Lista de todos los tratamientos para facilidad en las pruebas
        self.tratamientos = [
            self.tratamiento_analisis,
            self.tratamiento_vacunacion,
            self.tratamiento_desparasitacion,
            self.tratamiento_ecografia,
            self.tratamiento_limpieza,
            self.tratamiento_cirugia
        ]

    def test_dar_alta_varios_tratamientos(self):
        # Dar de alta cada tratamiento y verificar que esté en la lista
        for tratamiento in self.tratamientos:
            self.gestion.dar_alta_tratamiento(tratamiento)
            self.assertIn(tratamiento, self.gestion.tratamientos)
        
        # Verificar que todos los tratamientos están en la lista
        self.assertEqual(len(self.gestion.tratamientos), len(self.tratamientos))

    def test_dar_alta_tratamientos_duplicados(self):
        # Dar de alta un tratamiento y luego intentar darlo de alta de nuevo
        self.gestion.dar_alta_tratamiento(self.tratamiento_analisis)
        self.assertIn(self.tratamiento_analisis, self.gestion.tratamientos)
        
        # Intentar añadir el mismo tratamiento de nuevo
        self.gestion.dar_alta_tratamiento(self.tratamiento_analisis)
        # Verificar que solo haya un tratamiento en la lista
        self.assertEqual(len(self.gestion.tratamientos), 1)

    def test_dar_baja_tratamientos(self):
        # Dar de alta todos los tratamientos
        for tratamiento in self.tratamientos:
            self.gestion.dar_alta_tratamiento(tratamiento)

        # Dar de baja cada tratamiento y verificar que sea eliminado
        for tratamiento in self.tratamientos:
            self.gestion.dar_baja_tratamiento(tratamiento.nombre)
            self.assertNotIn(tratamiento, self.gestion.tratamientos)

        # Al final, la lista de tratamientos debería estar vacía
        self.assertEqual(len(self.gestion.tratamientos), 0)

    def test_dar_baja_tratamiento_inexistente(self):
        # Intentar dar de baja un tratamiento que no existe
        self.gestion.dar_baja_tratamiento("Tratamiento Inexistente")
        # La lista de tratamientos debería permanecer vacía
        self.assertEqual(len(self.gestion.tratamientos), 0)

    def test_mostrar_tratamientos(self):
        # Dar de alta todos los tratamientos
        for tratamiento in self.tratamientos:
            self.gestion.dar_alta_tratamiento(tratamiento)

        # Verificar que el número de tratamientos en la lista es correcto
        self.assertEqual(len(self.gestion.tratamientos), len(self.tratamientos))

        # Verificar que los tratamientos están en el orden esperado
        for i, tratamiento in enumerate(self.tratamientos):
            self.assertEqual(self.gestion.tratamientos[i].nombre, tratamiento.nombre)

if __name__ == "__main__":
    unittest.main()
