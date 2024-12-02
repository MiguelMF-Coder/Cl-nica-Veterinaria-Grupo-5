import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import requests
import logging

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validar_tratamiento(nombre_tratamiento, descripcion, precio):
    """
    Valida los datos de un tratamiento
    """
    if not nombre_tratamiento or not descripcion:
        return False, "Por favor, complete todos los campos obligatorios"
    if len(nombre_tratamiento) > 100:
        return False, "El nombre del tratamiento no debe exceder los 100 caracteres"
    if len(descripcion) > 200:
        return False, "La descripción no debe exceder los 200 caracteres"
    if precio < 0:
        return False, "El precio no puede ser negativo"
    return True, ""

def show():
    """
    Muestra la interfaz de gestión de tratamientos
    """
    st.title("Gestión de Tratamientos 🏥")

    # Crear las pestañas para la navegación
    tabs = st.tabs(["Nuevo Tratamiento", "Lista de Tratamientos"])

    with tabs[0]:
        show_new_treatment()

    with tabs[1]:
        show_treatment_list()

def show_new_treatment():
    """
    Muestra el formulario para registrar un nuevo tratamiento
    """
    st.subheader("📝 Registrar Nuevo Tratamiento")

    # Estilo personalizado con un borde para el formulario
    st.markdown("""
        <style>
        .form-container {
            border: 2px solid #ddd;
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            background-color: #f8f9fa;
        }
        .form-title {
            color: #FF6F61;
            font-weight: bold;
            font-size: 22px;
        }
        .btn-center {
            display: flex;
            justify-content: center;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="form-title">📝 Complete la Información del Tratamiento</div>', unsafe_allow_html=True)
        add_vertical_space(1)

        with st.form("form_nuevo_tratamiento", clear_on_submit=True):
            nombre_tratamiento = st.text_input("📄 Nombre del Tratamiento")
            descripcion = st.text_area("📋 Descripción")
            precio = st.number_input("💰 Precio (€)", min_value=0.0, step=0.1)

            col1, col2 = st.columns([4.7, 2])
            with col2:
                submitted = st.form_submit_button("Registrar", type="primary")

        st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        valido, mensaje = validar_tratamiento(nombre_tratamiento, descripcion, precio)
        if not valido:
            st.error(mensaje)
            return

        try:
            tratamiento_data = {
                "nombre_tratamiento": nombre_tratamiento,
                "descripcion": descripcion,
                "precio": precio
            }

            response = requests.post("http://localhost:8000/tratamientos/", json=tratamiento_data)
            if response.status_code == 201:
                st.success("¡Tratamiento registrado exitosamente! 🥳")
            else:
                st.error(f"❌ Error al registrar el tratamiento: {response.text}")
        except Exception as e:
            st.error(f"⚠️ Error al procesar el registro: {str(e)}")

def show_treatment_list():
    """
    Muestra la lista de tratamientos con filtros
    """
    st.title("📋 Lista de Tratamientos")

    # Filtros en una fila
    col1, col2 = st.columns(2)
    with col1:
        nombre_filtro = st.text_input(
            label="Filtrar por Nombre del Tratamiento",
            key="nombre_filtro",
            placeholder="Nombre del Tratamiento",
            label_visibility="hidden"
        )
    with col2:
        precio_filtro = st.number_input(
            label="Filtrar por Precio (€)",
            key="precio_filtro",
            min_value=0.0,
            step=0.1,
            format="%.2f",
            label_visibility="hidden"
        )

    try:
        # Obtener todos los tratamientos
        response = requests.get("http://localhost:8000/tratamientos/")
        if response.status_code == 200:
            tratamientos = response.json()
            if tratamientos:
                tratamientos_filtrados = [
                    t for t in tratamientos
                    if (not nombre_filtro or nombre_filtro.lower() in t['nombre_tratamiento'].lower()) and
                       (precio_filtro == 0 or t['precio'] == precio_filtro)
                ]

                if not tratamientos_filtrados:
                    st.info("No se encontraron tratamientos con los filtros especificados")
                    return

                for tratamiento in tratamientos_filtrados:
                    st.markdown("""
                        <style>
                            .tratamiento-card {
                                border: 1px solid #ddd;
                                border-radius: 10px;
                                padding: 15px;
                                margin-bottom: 20px;
                                background-color: #f8f9fa;
                                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
                            }
                        </style>
                        """, unsafe_allow_html=True)

                    with st.container():
                        st.markdown('<div class="tratamiento-card">', unsafe_allow_html=True)

                        col1, col2, col3 = st.columns([3, 2, 1])
                        
                        with col1:
                            st.markdown(f"### 📄 {tratamiento['nombre_tratamiento']}")
                            st.write(f"📋 **Descripción:** {tratamiento['descripcion']}")
                        
                        with col2:
                            st.write(f"💰 **Precio:** {tratamiento['precio']:.2f} €")
                            
                        with col3:
                            col_edit, col_delete = st.columns(2)
                            with col_edit:
                                if st.button("✏️", key=f"edit_{tratamiento['id_tratamiento']}"):
                                    show_edit_form(tratamiento)
                            with col_delete:
                                if st.button("❌", key=f"delete_{tratamiento['id_tratamiento']}"):
                                    delete_treatment(tratamiento['id_tratamiento'])

                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No hay tratamientos registrados")
        else:
            st.error("Error al cargar la lista de tratamientos")
    except Exception as e:
        st.error(f"Error: {str(e)}")

@st.dialog("Editar Tratamiento")
def show_edit_form(tratamiento):
    """
    Muestra un formulario para editar un tratamiento
    """
    with st.form("form_editar_tratamiento"):
        nombre = st.text_input("📄 Nombre del Tratamiento", value=tratamiento['nombre_tratamiento'])
        descripcion = st.text_area("📋 Descripción", value=tratamiento['descripcion'])
        precio = st.number_input("��� Precio (€)", min_value=0.0, step=0.1, value=tratamiento['precio'])
        
        submitted = st.form_submit_button("Guardar Cambios")
        if submitted:
            valido, mensaje = validar_tratamiento(nombre, descripcion, precio)
            if not valido:
                st.error(mensaje)
                return

            tratamiento_actualizado = {
                "nombre_tratamiento": nombre,
                "descripcion": descripcion,
                "precio": precio
            }
            
            response = requests.put(
                f"http://localhost:8000/tratamientos/{tratamiento['id_tratamiento']}", 
                json=tratamiento_actualizado
            )
            
            if response.status_code == 200:
                st.success("Tratamiento actualizado exitosamente")
                st.experimental_rerun()
            else:
                st.error("Error al actualizar el tratamiento")

def delete_treatment(id_tratamiento):
    """
    Elimina un tratamiento
    """
    try:
        response = requests.delete(f"http://localhost:8000/tratamientos/{id_tratamiento}")
        if response.status_code == 200:
            st.success("Tratamiento eliminado exitosamente")
            st.experimental_rerun()
        else:
            st.error("Error al eliminar el tratamiento")
    except Exception as e:
        st.error(f"Error al eliminar el tratamiento: {str(e)}")

if __name__ == "__main__":
    show()