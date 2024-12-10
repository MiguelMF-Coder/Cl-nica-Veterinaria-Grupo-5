import streamlit as st
from datetime import datetime

def show():
    # CSS personalizado para mejorar el diseño
    st.markdown("""
    <style>
        /* Estilo para títulos */
        h1, h2, h3 {
            color: #2563eb;
            margin-bottom: 1.5rem !important;
        }
        
        /* Estilo para cards de servicios */
        .service-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            height: 100%;
        }
        
        .service-card h3 {
            color: #1f2937;
            font-size: 1.25rem;
            margin-bottom: 1rem;
        }
        
        /* Estilo para información de contacto */
        .contact-info {
            background-color: #f8fafc;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #e5e7eb;
        }
        
        /* Estilo para el formulario */
        .form-container {
            background-color: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
        }
        
        /* Estilo para el pie de página */
        .footer {
            text-align: center;
            padding: 2rem 0;
            color: #6b7280;
            font-size: 0.875rem;
        }
        
        /* Estilo para horarios */
        .schedule-card {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 2rem 0;
        }
        
        .schedule-card h2 {
            color: white !important;
            margin-bottom: 1rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Encabezado principal con imagen
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("")
        st.image("streamlit/logo.jpg", use_container_width=True)
    with col2:
        st.title("Bienvenidos a la Clínica Veterinaria UFVVet 🐾")
        st.markdown("""
        <div style='font-size: 1.1rem; color: #4b5563; margin-bottom: 2rem;'>
        En <strong>UFVVet</strong>, nos preocupamos por el bienestar y la salud de tus mascotas. 
        Ofrecemos servicios de alta calidad y un equipo de profesionales dedicados a brindar la mejor atención posible.
        </div>
        """, unsafe_allow_html=True)

    # Servicios destacados con cards
    st.header("Nuestros Servicios")
    cols = st.columns(3)
    servicios = [
        ("🏥 Consultas generales", "Ofrecemos atención primaria y seguimiento personalizado de la salud de tus mascotas, garantizando su bienestar integral."),
        ("💉 Vacunación y desparasitación", "Protege a tu mascota con nuestro programa completo de vacunación y control de parásitos, siguiendo los más altos estándares."),
        ("⚕️ Cirugías especializadas", "Nuestro equipo quirúrgico experto y tecnología de vanguardia garantizan la mejor atención en intervenciones quirúrgicas."),
    ]

    for col, (titulo, descripcion) in zip(cols, servicios):
        with col:
            st.markdown(f"""
            <div class="service-card">
                <h3>{titulo}</h3>
                <p style='color: #4b5563;'>{descripcion}</p>
            </div>
            """, unsafe_allow_html=True)

    # Horarios en un diseño más atractivo
    st.markdown("""
    <div class="schedule-card">
        <h2>📅 Horarios de Atención</h2>
        <div style='font-size: 1.1rem;'>
            ⏰ Lunes a Viernes: 8:00 AM - 8:00 PM<br>
            ⏰ Sábados: 9:00 AM - 3:00 PM<br>
            ⏰ Domingos y festivos: Cerrado
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Información de contacto y formulario en columnas
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("📞 Contáctanos")
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown("")
        st.markdown("")
        st.markdown("""
        <div class="contact-info">
            <p><strong>📱 Teléfono:</strong> +34 123 456 789</p>
            <p><strong>📧 Email:</strong> contacto@ufvvet.com</p>
            <p><strong>📍 Dirección:</strong> Calle de la Mascota Feliz, 123, Madrid, España</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.header("✉️ Datos de contacto")
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown("")
        st.markdown("")
        with st.form("form_cita"):
            nombre = st.text_input("👤 Nombre")
            email = st.text_input("📧 Email")
            motivo = st.text_area("📝 Motivo de la consulta")
            enviar = st.form_submit_button("Enviar solicitud")
            
            if enviar and nombre and email and motivo:
                st.success("✅ Tu solicitud ha sido enviada. Nos pondremos en contacto contigo pronto.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Pie de página mejorado
    st.markdown("---")
    st.markdown(f"""
    <div class="footer">
        © {datetime.now().year} UFVVet. Todos los derechos reservados.<br>
        Cuidando de tus mascotas con profesionalidad y cariño.
    </div>
    """, unsafe_allow_html=True)