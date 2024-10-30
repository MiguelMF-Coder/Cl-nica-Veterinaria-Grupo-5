import unittest
from cliente import Cliente, Mascota, GestionClientes

class TestGestionClientes(unittest.TestCase):
    def setUp(self):
        # Configura un entorno de prueba con una instancia de GestionClientes
        self.gestion = GestionClientes()
        
        # Crear clientes y mascotas
        self.cliente1 = Cliente("Laura", "12345678A", "600123456", "Calle Falsa 123")
        self.mascota1 = Mascota("Firulais", "Labrador", 3)
        
        self.cliente2 = Cliente("Carlos", "87654321B", "699987654", "Avenida Siempreviva 742")
        self.mascota2 = Mascota("Pelusa", "Siames", 5)

    def test_registrar_cliente(self):
        # Prueba para registrar un cliente
        self.gestion.registrar_cliente(self.cliente1)
        self.assertIn(self.cliente1, self.gestion.clientes)

        # Intentar registrar un cliente duplicado
        self.gestion.registrar_cliente(self.cliente1)
        self.assertEqual(len(self.gestion.clientes), 1)  # Solo debería haber un cliente

    def test_buscar_cliente(self):
        # Registrar clientes
        self.gestion.registrar_cliente(self.cliente1)
        self.gestion.registrar_cliente(self.cliente2)

        # Buscar cliente por DNI
        cliente = self.gestion.buscar_cliente(dni="12345678A")
        self.assertEqual(cliente, self.cliente1)

        # Buscar cliente por teléfono
        cliente = self.gestion.buscar_cliente(telefono="699987654")
        self.assertEqual(cliente, self.cliente2)

        # Intentar buscar un cliente inexistente
        cliente = self.gestion.buscar_cliente(dni="00000000C")
        self.assertIsNone(cliente)

    def test_registrar_mascota(self):
        # Registrar cliente y mascota
        self.gestion.registrar_cliente(self.cliente1)
        self.gestion.registrar_mascota(self.cliente1, self.mascota1)
        
        # Verificar que la mascota se ha añadido al cliente
        self.assertIn(self.mascota1, self.cliente1.mascotas)

    def test_marcar_mascota_como_fallecida(self):
        # Registrar cliente y mascota
        self.gestion.registrar_cliente(self.cliente1)
        self.gestion.registrar_mascota(self.cliente1, self.mascota1)
        
        # Marcar la mascota como fallecida
        self.gestion.marcar_mascota_como_fallecida(self.cliente1, "Firulais")
        self.assertEqual(self.mascota1.estado, "Fallecido")

        # Intentar marcar una mascota inexistente como fallecida
        self.gestion.marcar_mascota_como_fallecida(self.cliente1, "Inexistente")
        # Verificación: el estado de Firulais sigue siendo "Fallecido" y no afecta a otras mascotas
        self.assertEqual(self.mascota1.estado, "Fallecido")

    def test_ver_todos_los_clientes(self):
        # Registrar clientes y mascotas
        self.gestion.registrar_cliente(self.cliente1)
        self.gestion.registrar_mascota(self.cliente1, self.mascota1)
        
        self.gestion.registrar_cliente(self.cliente2)
        self.gestion.registrar_mascota(self.cliente2, self.mascota2)

        # Usar un conteo para verificar el total de clientes y mascotas
        total_clientes = len(self.gestion.clientes)
        total_mascotas = sum(len(cliente.mascotas) for cliente in self.gestion.clientes)

        self.assertEqual(total_clientes, 2)
        self.assertEqual(total_mascotas, 2)

if __name__ == "__main__":
    unittest.main()
