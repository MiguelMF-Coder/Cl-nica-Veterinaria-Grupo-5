import streamlit as st

def show():
        
    # Logo e imagen de bienvenida
    st.image("streamlit/logo.jpg", use_column_width=True)
    st.title("Bienvenidos a la Clínica Veterinaria UFVVet 🐾")
    st.write(
        """
        En **UFVVet**, nos preocupamos por el bienestar y la salud de tus mascotas. Ofrecemos servicios de alta calidad y 
        un equipo de profesionales dedicados a brindar la mejor atención posible.
        """
    )

    # Sección de servicios destacados
    st.header("Nuestros Servicios")
    cols = st.columns(3)
    servicios = [
        ("Consultas generales", "Ofrecemos atención primaria y seguimiento de la salud de tus mascotas."),
        ("Vacunación y desparasitación", "Mantén a tu mascota protegida y sana con nuestros servicios de vacunación."),
        ("Cirugías especializadas", "Contamos con quirófanos equipados y un equipo experto en intervenciones quirúrgicas."),
    ]

    for col, (titulo, descripcion) in zip(cols, servicios):
        with col:
            st.subheader(titulo)
            st.write(descripcion)

    # Horarios y contacto
    st.header("Horarios de Atención")
    st.write(
        """
        - Lunes a Viernes: 8:00 AM - 8:00 PM
        - Sábados: 9:00 AM - 3:00 PM
        - Domingos y festivos: Cerrado
        """
    )

    st.header("Contáctanos")
    st.write(
        """
        Teléfono: +34 123 456 789 \n
        Email: contacto@ufVVet.com \n
        Dirección: Calle de la Mascota Feliz, 123, Madrid, España
        """
    )

    # Formulario de datos de contacto
    st.header("Dejanos tu contacto")
    with st.form("form_cita"):
        nombre = st.text_input("Nombre")
        email = st.text_input("Email")
        motivo = st.text_area("Motivo de la consulta")
        enviar = st.form_submit_button("Enviar")

        if enviar:
            st.success("Tu solicitud de cita ha sido enviada. Nos pondremos en contacto contigo pronto.")

    # Pie de página
    st.markdown("---")
    st.write("© 2024 UFVVet. Todos los derechos reservados.")
    pass