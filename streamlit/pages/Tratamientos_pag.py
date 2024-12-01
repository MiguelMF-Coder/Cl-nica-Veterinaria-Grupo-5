import streamlit as st
from clinica.services.gestion_tratamiento import GestionTratamientos, Tratamiento
from clinica.dbconfig import get_db
from sqlalchemy.orm import Session

def show():
    # Título de la página
    st.title("Gestión de Tratamientos")

    # Get the database session
    db: Session = next(get_db())

    # Instancia de la gestión de tratamientos
    gestion_tratamientos = GestionTratamientos(db)

    # Formulario para registrar un nuevo tratamiento
    st.header("Registrar Nuevo Tratamiento")
    with st.form("form_dar_alta_tratamiento"):
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
                gestion_tratamientos.dar_alta_tratamiento(nuevo_tratamiento)
                st.success(f"Tratamiento '{nombre_tratamiento}' registrado exitosamente.")
            else:
                st.error("Por favor, completa todos los campos obligatorios.")

    # Visualización de tratamientos registrados
    st.header("Tratamientos Registrados")
    if st.button("Ver Tratamientos"):
        tratamientos = gestion_tratamientos.listar_tratamientos()  # Supongo que tienes esta función
        if tratamientos:
            for tratamiento in tratamientos:
                st.write(f"Nombre: {tratamiento.nombre_tratamiento}, Precio: {tratamiento.precio}€, Descripción: {tratamiento.descripcion}")
        else:
            st.info("No hay tratamientos registrados.")