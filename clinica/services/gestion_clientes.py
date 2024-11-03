import re  # Librería de expresiones regulares para validaciones

class Mascota:
    def __init__(self, nombre, raza, edad):
        self.nombre = nombre
        self.raza = raza
        self.edad = edad
        self.historial_clinico = []
        self.estado = "Vivo"  # Estado inicial de la mascota

    def agregar_historial(self, entrada):
        """Agrega una entrada al historial clínico de la mascota."""
        self.historial_clinico.append(entrada)

    def marcar_como_fallecido(self):
        """Marca a la mascota como fallecida."""
        self.estado = "Fallecido"

    def __str__(self):
        return f"{self.nombre} - Raza: {self.raza}, Edad: {self.edad} años, Estado: {self.estado}"


class Cliente:
    def __init__(self, nombre, dni, telefono, direccion):
        self.nombre = nombre
        self.dni = dni
        self.telefono = telefono
        self.direccion = direccion
        self.mascotas = []

    def agregar_mascota(self, mascota):
        """Agrega una mascota a la lista de mascotas del cliente."""
        self.mascotas.append(mascota)

    def buscar_mascota(self, nombre):
        """Busca una mascota por su nombre en la lista de mascotas del cliente."""
        for mascota in self.mascotas:
            if mascota.nombre == nombre:
                return mascota
        return None

    def __str__(self):
        mascotas_info = ", ".join([mascota.nombre for mascota in self.mascotas])
        return f"{self.nombre} - DNI: {self.dni}, Teléfono: {self.telefono}, Dirección: {self.direccion}, Mascotas: {mascotas_info}"


class GestionClientes:
    def __init__(self):
        self.clientes = []

    def registrar_cliente(self, cliente):
        """Registra un nuevo cliente en la lista de clientes."""
        if any(c.dni == cliente.dni or c.telefono == cliente.telefono for c in self.clientes):
            print(f"El cliente con DNI '{cliente.dni}' o Teléfono '{cliente.telefono}' ya está registrado.")
        else:
            self.clientes.append(cliente)
            print(f"Cliente '{cliente.nombre}' registrado con éxito.")

    def buscar_cliente(self, dni=None, telefono=None):
        """Busca un cliente por DNI o teléfono y devuelve el cliente encontrado."""
        for cliente in self.clientes:
            if (dni and cliente.dni == dni) or (telefono and cliente.telefono == telefono):
                return cliente
        return None

    def mostrar_cliente(self, cliente):
        """Muestra la información del cliente y sus mascotas."""
        if cliente:
            print(cliente)
            for mascota in cliente.mascotas:
                print(f"  {mascota}")
                for entrada in mascota.historial_clinico:
                    print(f"    Historial: {entrada}")
        else:
            print("Cliente no encontrado.")

    def registrar_mascota(self, cliente, mascota):
        """Registra una nueva mascota para un cliente existente."""
        if cliente:
            cliente.agregar_mascota(mascota)
            print(f"Mascota '{mascota.nombre}' registrada para el cliente '{cliente.nombre}'.")
        else:
            print("Cliente no encontrado.")

    def marcar_mascota_como_fallecido(self, cliente, nombre_mascota):
        """Marca una mascota como fallecida para un cliente específico."""
        mascota = cliente.buscar_mascota(nombre_mascota)
        if mascota:
            mascota.marcar_como_fallecido()
            print(f"La mascota '{mascota.nombre}' ha sido marcada como fallecida.")
        else:
            print(f"No se encontró la mascota '{nombre_mascota}' para el cliente '{cliente.nombre}'.")


# Función para mostrar el menú y realizar operaciones
def mostrar_menu():
    print("\n--- Menú de Gestión de Clientes ---")
    print("1. Buscar cliente por DNI o teléfono")
    print("2. Registrar nuevo cliente y mascota")
    print("3. Registrar mascota para cliente existente")
    print("4. Marcar mascota como fallecida")
    print("5. Salir")
    return input("Seleccione una opción (1-5): ")


# Código principal (sin if __name__ == "__main__")
gestion = GestionClientes()

# Bucle del menú
while True:
    opcion = mostrar_menu()

    if opcion == '1':
        # Buscar cliente por DNI o teléfono
        criterio = input("Buscar por (1) DNI o (2) Teléfono: ")
        if criterio == '1':
            dni = input("Ingrese el DNI del cliente: ").strip()
            if not re.match(r"^\d{8}[A-Za-z]$", dni):
                print("Error: DNI debe tener 8 números seguidos de una letra.")
                continue
            cliente = gestion.buscar_cliente(dni=dni)
        elif criterio == '2':
            telefono = input("Ingrese el teléfono del cliente: ").strip()
            if not re.match(r"^\d{9}$", telefono):
                print("Error: El teléfono debe tener exactamente 9 dígitos.")
                continue
            cliente = gestion.buscar_cliente(telefono=telefono)
        else:
            print("Opción no válida.")
            continue
        gestion.mostrar_cliente(cliente)

    elif opcion == '2':
        # Registrar nuevo cliente y mascota
        try:
            # Validar nombre del cliente
            nombre_cliente = input("Ingrese el nombre del cliente: ").strip()
            if not nombre_cliente or not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", nombre_cliente):
                raise ValueError("El nombre del cliente solo puede contener letras y espacios.")

            # Validar DNI
            dni = input("Ingrese el DNI del cliente: ").strip()
            if not re.match(r"^\d{8}[A-Za-z]$", dni):
                raise ValueError("DNI debe tener 8 números seguidos de una letra.")

            # Validar Teléfono
            telefono = input("Ingrese el teléfono del cliente: ").strip()
            if not re.match(r"^\d{9}$", telefono):
                raise ValueError("El teléfono debe tener exactamente 9 dígitos.")

            # Validar Dirección
            direccion = input("Ingrese la dirección del cliente: ").strip()
            if not direccion:
                raise ValueError("La dirección no puede estar vacía.")
            cliente = Cliente(nombre_cliente, dni, telefono, direccion)

            # Validar nombre, raza y edad de la mascota
            nombre_mascota = input("Ingrese el nombre de la mascota: ").strip()
            if not nombre_mascota or not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", nombre_mascota):
                raise ValueError("El nombre de la mascota solo puede contener letras y espacios.")

            raza = input("Ingrese la raza de la mascota: ").strip()
            if not raza or not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", raza):
                raise ValueError("La raza de la mascota solo puede contener letras y espacios.")

            edad = input("Ingrese la edad de la mascota: ").strip()
            if not edad.isdigit() or int(edad) <= 0:
                raise ValueError("La edad debe ser un número positivo.")
            edad = int(edad)
            mascota = Mascota(nombre_mascota, raza, edad)

            cliente.agregar_mascota(mascota)
            gestion.registrar_cliente(cliente)
        except ValueError as e:
            print(f"Error: {e}")

    elif opcion == '3':
        # Registrar mascota para cliente existente
        dni = input("Ingrese el DNI del cliente: ").strip()
        if not re.match(r"^\d{8}[A-Za-z]$", dni):
            print("Error: DNI debe tener 8 números seguidos de una letra.")
            continue
        cliente = gestion.buscar_cliente(dni=dni)
        if cliente:
            try:
                nombre_mascota = input("Ingrese el nombre de la nueva mascota: ").strip()
                if not nombre_mascota or not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", nombre_mascota):
                    raise ValueError("El nombre de la mascota solo puede contener letras y espacios.")

                raza = input("Ingrese la raza de la mascota: ").strip()
                if not raza or not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", raza):
                    raise ValueError("La raza de la mascota solo puede contener letras y espacios.")

                edad = input("Ingrese la edad de la mascota: ").strip()
                if not edad.isdigit() or int(edad) <= 0:
                    raise ValueError("La edad debe ser un número positivo.")
                edad = int(edad)
                mascota = Mascota(nombre_mascota, raza, edad)
                gestion.registrar_mascota(cliente, mascota)
            except ValueError as e:
                print(f"Error: {e}")
        else:
            print("Cliente no encontrado.")

    elif opcion == '4':
        # Marcar mascota como fallecida
        dni = input("Ingrese el DNI del cliente: ").strip()
        if not re.match(r"^\d{8}[A-Za-z]$", dni):
            print("Error: DNI debe tener 8 números seguidos de una letra.")
            continue
        cliente = gestion.buscar_cliente(dni=dni)
        if cliente:
            nombre_mascota = input("Ingrese el nombre de la mascota a marcar como fallecida: ").strip()
            gestion.marcar_mascota_como_fallecida(cliente, nombre_mascota)
        else:
            print("Cliente no encontrado.")

    elif opcion == '5':
        print("Saliendo del sistema de gestión de clientes.")
        break

    else:
        print("Opción no válida. Por favor, seleccione una opción entre 1 y 5.")
