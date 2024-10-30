# tratamiento.py

class Tratamiento:
    def __init__(self, nombre, descripcion, precio):
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio

    def __str__(self):
        return f"{self.nombre} - {self.descripcion} - Precio: {self.precio}€"


class GestionTratamientos:
    def __init__(self):
        self.tratamientos = []

    def dar_alta_tratamiento(self, tratamiento):
        if any(t.nombre == tratamiento.nombre for t in self.tratamientos):
            print(f"Error: El tratamiento '{tratamiento.nombre}' ya está registrado.")
        else:
            self.tratamientos.append(tratamiento)
            print(f"Tratamiento '{tratamiento.nombre}' dado de alta con éxito.")

    def dar_baja_tratamiento(self, nombre):
        for tratamiento in self.tratamientos:
            if tratamiento.nombre == nombre:
                self.tratamientos.remove(tratamiento)
                print(f"Tratamiento '{nombre}' dado de baja con éxito.")
                return
        print(f"Error: No se encontró el tratamiento '{nombre}'.")

    def mostrar_tratamientos(self):
        if not self.tratamientos:
            print("No hay tratamientos registrados.")
        else:
            print("Tratamientos disponibles:")
            for tratamiento in self.tratamientos:
                print(tratamiento)


# Función para mostrar el menú y realizar operaciones
def mostrar_menu():
    print("\n--- Menú de Gestión de Tratamientos ---")
    print("1. Mostrar tratamientos disponibles")
    print("2. Dar de alta un tratamiento")
    print("3. Dar de baja un tratamiento")
    print("4. Salir")
    return input("Seleccione una opción (1-4): ")


# Código principal (sin el bloque if __name__ == "__main__")
gestion = GestionTratamientos()

# Tratamientos predefinidos
tratamientos_iniciales = [
    Tratamiento("Análisis", "Análisis de sangre, orina, etc.", 50),
    Tratamiento("Vacunación", "Vacunación general para perros y gatos", 30),
    Tratamiento("Desparasitación", "Desparasitación interna y externa", 25),
    Tratamiento("Ecografías", "Ecografía abdominal y torácica", 100),
    Tratamiento("Limpieza dental", "Limpieza dental para evitar enfermedades bucales", 75),
    Tratamiento("Cirugía básica - Castración", "Castración de perros y gatos", 200)
]

# Dar de alta los tratamientos iniciales
for tratamiento in tratamientos_iniciales:
    gestion.dar_alta_tratamiento(tratamiento)

# Loop del menú con control de errores
while True:
    opcion = mostrar_menu()

    if opcion == '1':
        gestion.mostrar_tratamientos()

    elif opcion == '2':
        try:
            nombre = input("Ingrese el nombre del tratamiento: ").strip()
            if not nombre:
                raise ValueError("El nombre del tratamiento no puede estar vacío.")

            descripcion = input("Ingrese la descripción del tratamiento: ").strip()
            if not descripcion:
                raise ValueError("La descripción del tratamiento no puede estar vacía.")

            precio = input("Ingrese el precio del tratamiento: ").strip()
            if not precio.replace('.', '', 1).isdigit():
                raise ValueError("El precio debe ser un número válido.")
            precio = float(precio)

            nuevo_tratamiento = Tratamiento(nombre, descripcion, precio)
            gestion.dar_alta_tratamiento(nuevo_tratamiento)
        except ValueError as e:
            print(f"Error: {e}")

    elif opcion == '3':
        try:
            nombre = input("Ingrese el nombre del tratamiento a dar de baja: ").strip()
            if not nombre:
                raise ValueError("El nombre del tratamiento no puede estar vacío.")
            gestion.dar_baja_tratamiento(nombre)
        except ValueError as e:
            print(f"Error: {e}")

    elif opcion == '4':
        print("Saliendo del sistema de gestión de tratamientos.")
        break

    else:
        print("Opción no válida. Por favor, seleccione una opción entre 1 y 4.")
