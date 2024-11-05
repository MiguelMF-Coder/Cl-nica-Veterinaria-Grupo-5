import streamlit as st
from clinica.services.gestion_clientes import GestionClientes, Cliente, Mascota

def show():
        
    # Título de la página
    st.title("Gestión de Clientes")

    # Instancia de la gestión de clientes
    gestion_clientes = GestionClientes()

    # Formulario para registrar un cliente
    st.header("Registrar Nuevo Cliente")
    with st.form("form_registrar_cliente"):
        nombre = st.text_input("Nombre del Cliente", max_chars=50)
        edad = st.number_input("Edad", min_value=0, step=1)
        dni = st.text_input("DNI")
        direccion = st.text_input("Dirección")
        telefono = st.text_input("Teléfono", max_chars=15)
        
        # Botón de envío
        submit_button = st.form_submit_button("Registrar Cliente")
        
        if submit_button:
            if nombre and dni and direccion and telefono:
                # Crea un objeto Cliente
                nuevo_cliente = Cliente(nombre=nombre, edad=edad, dni=self.dni_unico, direccion=direccion, telefono=telefono)
                
                # Llama a la función de gestión de clientes para registrar
                gestion_clientes.registrar_cliente(nuevo_cliente)
                st.success(f"Cliente {nombre} registrado exitosamente.")
            else:
                st.error("Por favor, completa todos los campos obligatorios.")

    # Visualización de clientes registrados
    st.header("Clientes Registrados")
    if st.button("Ver Clientes"):
        clientes = gestion_clientes.obtener_clientes()  # Supongo que tienes esta función
        if clientes:
            for cliente in clientes:
                st.write(f"Nombre: {cliente.nombre}, DNI: {cliente.dni}, Teléfono: {cliente.telefono}")
        else:
            st.info("No hay clientes registrados.")
    pass