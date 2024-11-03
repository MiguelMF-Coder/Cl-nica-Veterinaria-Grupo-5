import re
from datetime import datetime

class Tratamiento:
    def __init__(self, nombre, descripcion, precio):
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio = precio

class Cita:
    def __init__(self, nombre_animal, nombre_dueno, tratamiento, fecha_hora):
        self.nombre_animal = nombre_animal
        self.nombre_dueno = nombre_dueno
        self.tratamiento = tratamiento
        self.fecha_hora = fecha_hora
        self.realizado = False
        self.factura = None

    def finalizar_cita(self, tratamientos_realizados):
        """Marca la cita como finalizada, generando una factura con los tratamientos realizados."""
        total = sum(tratamiento.precio for tratamiento in tratamientos_realizados)
        detalle_tratamientos = [(tratamiento.nombre, tratamiento.precio) for tratamiento in tratamientos_realizados]
        
        # Crear la factura con detalles específicos
        self.factura = Factura(
            fecha_hora=self.fecha_hora,
            nombre_animal=self.nombre_animal,
            nombre_dueno=self.nombre_dueno,
            tratamientos=detalle_tratamientos,
            total=total,
            metodo_pago=None  # Se establecerá posteriormente
        )
        self.realizado = True
        print("Cita finalizada y factura generada.")

    def __str__(self):
        estado = "Realizada" if self.realizado else "Pendiente"
        return f"{self.nombre_animal} con {self.nombre_dueno} para {self.tratamiento.nombre} - Fecha: {self.fecha_hora} - Estado: {estado}"


class Factura:
    def __init__(self, fecha_hora, nombre_animal, nombre_dueno, tratamientos, total, metodo_pago):
        self.fecha_hora = fecha_hora
        self.nombre_animal = nombre_animal
        self.nombre_dueno = nombre_dueno
        self.tratamientos = tratamientos
        self.total = total
        self.metodo_pago = metodo_pago

    def establecer_metodo_pago(self, metodo):
        if metodo.lower() not in ["efectivo", "tarjeta", "transferencia"]:
            raise ValueError("El método de pago debe ser 'efectivo', 'tarjeta' o 'transferencia'.")
        self.metodo_pago = metodo

    def __str__(self):
        tratamientos_str = "\n".join([f"- {nombre}: {precio}€" for nombre, precio in self.tratamientos])
        return (f"Factura:\nFecha y hora: {self.fecha_hora}\nDueño: {self.nombre_dueno}\nAnimal: {self.nombre_animal}\n"
                f"Tratamientos realizados:\n{tratamientos_str}\nTotal: {self.total}€\nMétodo de pago: {self.metodo_pago}")


class GestionCitas:
    def __init__(self):
        self.citas = []

    def registrar_cita(self, cita):
        """Registra una nueva cita, verificando que no exista una cita duplicada para el mismo animal, dueño y hora."""
        for c in self.citas:
            if (c.nombre_animal == cita.nombre_animal and c.nombre_dueno == cita.nombre_dueno and c.fecha_hora == cita.fecha_hora):
                raise ValueError("Ya existe una cita para este animal, dueño y horario.")
        self.citas.append(cita)
        print(f"Cita registrada para {cita.nombre_animal} con {cita.nombre_dueno}.")

    def ver_todas_las_citas(self):
        """Muestra todas las citas registradas en el sistema."""
        if not self.citas:
            print("No hay citas registradas.")
        else:
            print("\n--- Todas las Citas ---")
            for cita in self.citas:
                print(cita)

    def buscar_cita(self, nombre_animal, nombre_dueno):
        """Busca una cita por el nombre del animal y el dueño."""
        for cita in self.citas:
            if cita.nombre_animal == nombre_animal and cita.nombre_dueno == nombre_dueno:
                return cita
        return None

    def modificar_cita(self, cita, nuevo_tratamiento=None, nueva_fecha_hora=None):
        """Modifica el tratamiento o la fecha de una cita existente."""
        if nuevo_tratamiento:
            cita.tratamiento = nuevo_tratamiento
        if nueva_fecha_hora:
            cita.fecha_hora = nueva_fecha_hora
        print("Cita modificada con éxito.")

    def cancelar_cita(self, cita):
        """Cancela una cita eliminándola de la lista de citas."""
        self.citas.remove(cita)
        print("Cita cancelada con éxito.")

    def finalizar_cita(self, cita, tratamientos_realizados, metodo_pago):
        """Finaliza la cita y establece el método de pago en la factura."""
        cita.finalizar_cita(tratamientos_realizados)
        try:
            cita.factura.establecer_metodo_pago(metodo_pago)
        except ValueError as e:
            print(f"Error: {e}")
            return
        print("Método de pago registrado y cita finalizada.")
        print(cita.factura)


def solicitar_fecha_hora():
    """Solicita al usuario la fecha y hora parte por parte, y la convierte en un objeto datetime."""
    try:
        dia = int(input("Ingrese el día (1-31): ").strip())
        mes = int(input("Ingrese el mes (1-12): ").strip())
        anio = int(input("Ingrese el año (YYYY): ").strip())
        hora = int(input("Ingrese la hora (0-23): ").strip())
        minuto = int(input("Ingrese los minutos (0-59): ").strip())

        # Crear el objeto datetime y verificar si es válida
        fecha_hora = datetime(anio, mes, dia, hora, minuto)
        return fecha_hora
    except ValueError:
        print("Error: Fecha o hora inválida. Intente de nuevo.")
        return None


def mostrar_menu():
    print("\n--- Menú de Gestión de Citas ---")
    print("1. Registrar nueva cita")
    print("2. Modificar cita existente")
    print("3. Cancelar una cita")
    print("4. Finalizar una cita")
    print("5. Ver todas las citas")
    print("6. Salir")
    return input("Seleccione una opción (1-6): ")


gestion_citas = GestionCitas()

# Bucle del menú con control de errores
while True:
    opcion = mostrar_menu()

    if opcion == '1':
        # Registrar una nueva cita
        try:
            nombre_animal = input("Ingrese el nombre del animal: ").strip()
            if not re.match("^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", nombre_animal):
                raise ValueError("El nombre del animal solo puede contener letras y espacios.")

            nombre_dueno = input("Ingrese el nombre del dueño: ").strip()
            if not re.match("^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", nombre_dueno):
                raise ValueError("El nombre del dueño solo puede contener letras y espacios.")

            tratamiento_nombre = input("Ingrese el tratamiento solicitado: ").strip()
            tratamiento_precio = input("Ingrese el precio del tratamiento: ").strip()
            if not re.match(r"^\d+(\.\d{1,2})?$", tratamiento_precio) or float(tratamiento_precio) <= 0:
                raise ValueError("El precio debe ser un número positivo con hasta dos decimales.")
            tratamiento = Tratamiento(tratamiento_nombre, "Descripción del tratamiento", float(tratamiento_precio))

            # Solicitar la fecha y hora de la cita
            fecha_hora = None
            while not fecha_hora:
                fecha_hora = solicitar_fecha_hora()

            nueva_cita = Cita(nombre_animal, nombre_dueno, tratamiento, fecha_hora)
            gestion_citas.registrar_cita(nueva_cita)
        except ValueError as e:
            print(f"Error: {e}")

    elif opcion == '2':
        # Modificar una cita existente
        nombre_animal = input("Ingrese el nombre del animal: ").strip()
        nombre_dueno = input("Ingrese el nombre del dueño: ").strip()
        cita = gestion_citas.buscar_cita(nombre_animal, nombre_dueno)
        if cita:
            nuevo_tratamiento_nombre = input("Ingrese el nuevo tratamiento (dejar en blanco si no cambia): ").strip()
            if nuevo_tratamiento_nombre:
                nuevo_tratamiento_precio = input("Ingrese el precio del nuevo tratamiento: ").strip()
                if re.match(r"^\d+(\.\d{1,2})?$", nuevo_tratamiento_precio) and float(nuevo_tratamiento_precio) > 0:
                    nuevo_tratamiento = Tratamiento(nuevo_tratamiento_nombre, "Descripción del nuevo tratamiento", float(nuevo_tratamiento_precio))
                    gestion_citas.modificar_cita(cita, nuevo_tratamiento=nuevo_tratamiento)

            nueva_fecha_hora = None
            while not nueva_fecha_hora:
                nueva_fecha_hora = solicitar_fecha_hora()
            gestion_citas.modificar_cita(cita, nueva_fecha_hora=nueva_fecha_hora)
        else:
            print("Cita no encontrada.")

    elif opcion == '3':
        # Cancelar una cita
        nombre_animal = input("Ingrese el nombre del animal: ").strip()
        nombre_dueno = input("Ingrese el nombre del dueño: ").strip()
        cita = gestion_citas.buscar_cita(nombre_animal, nombre_dueno)
        if cita:
            gestion_citas.cancelar_cita(cita)
        else:
            print("Cita no encontrada.")

    elif opcion == '4':
        # Finalizar una cita
        nombre_animal = input("Ingrese el nombre del animal: ").strip()
        nombre_dueno = input("Ingrese el nombre del dueño: ").strip()
        cita = gestion_citas.buscar_cita(nombre_animal, nombre_dueno)
        if cita:
            if cita.realizado:
                print("La cita ya ha sido finalizada.")
            else:
                try:
                    metodo_pago = input("Ingrese el método de pago (efectivo, tarjeta, transferencia): ").strip().lower()
                    gestion_citas.finalizar_cita(cita, [cita.tratamiento], metodo_pago)
                except ValueError as e:
                    print(f"Error: {e}")
        else:
            print("Cita no encontrada.")

    elif opcion == '5':
        # Ver todas las citas
        gestion_citas.ver_todas_las_citas()

    elif opcion == '6':
        print("Saliendo del sistema de gestión de citas.")
        break

    else:
        print("Opción no válida. Por favor, seleccione una opción entre 1 y 6.")
