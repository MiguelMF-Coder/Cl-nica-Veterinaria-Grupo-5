import streamlit as st
from clinica.services.gestion_tratamiento import GestionTratamientos, Tratamiento

def show():
    # Título de la página
    st.title("Gestión de Tratamientos")

    # Instancia de la gestión de tratamientos
    gestion_tratamientos = GestionTratamientos()

    # Formulario para registrar un nuevo tratamiento
    st.header("Registrar Nuevo Tratamiento")
    with st.form("form_registrar_tratamiento"):
        nombre_tratamiento = st.text_input("Nombre del Tratamiento", max_chars=50)
        descripcion = st.text_area("Descripción")
        precio = st.number_input("Precio (€)", min_value=0.0, step=0.1)

        # Botón de envío
        submit_button = st.form_submit_button("Registrar Tratamiento")
        
        if submit_button:
            if nombre_tratamiento and descripcion:
                # Crea un objeto Tratamiento
                nuevo_tratamiento = Tratamiento(nombre=nombre_tratamiento, descripcion=descripcion, precio=precio)
                
                # Llama a la función de gestión de tratamientos para registrar
                gestion_tratamientos.registrar_tratamiento(nuevo_tratamiento)
                st.success(f"Tratamiento '{nombre_tratamiento}' registrado exitosamente.")
            else:
                st.error("Por favor, completa todos los campos obligatorios.")

    # Visualización de tratamientos registrados
    st.header("Tratamientos Registrados")
    if st.button("Ver Tratamientos"):
        tratamientos = gestion_tratamientos.obtener_tratamientos()  # Supongo que tienes esta función
        if tratamientos:
            for tratamiento in tratamientos:
                st.write(f"Nombre: {tratamiento.nombre}, Precio: {tratamiento.precio}€, Descripción: {tratamiento.descripcion}")
        else:
            st.info("No hay tratamientos registrados.")
    pass