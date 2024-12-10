import streamlit as st
import requests
import logging
from datetime import datetime
from streamlit_extras.add_vertical_space import add_vertical_space
from clinica.services.gestion_tratamiento import GestionTratamientos
from clinica.dbconfig import get_db
from sqlalchemy.orm import Session

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validar_tratamiento(nombre_tratamiento, descripcion, precio, estado, id_cliente):
    """
    Valida los datos de un tratamiento
    """
    if not all([nombre_tratamiento, descripcion, estado, id_cliente]):
        return False, "Por favor, complete todos los campos obligatorios"
    if len(nombre_tratamiento) > 100:
        return False, "El nombre del tratamiento no debe exceder los 100 caracteres"
    if len(descripcion) > 500:
        return False, "La descripción no debe exceder los 500 caracteres"
    if precio < 0:
        return False, "El precio no puede ser negativo"
    if estado not in ["Activo", "Finalizada", "Cancelada"]:
        return False, "Estado no válido"
    return True, ""

def show():
    """
    Muestra la interfaz de gestión de tratamientos
    """

    st.markdown("""
    <style>
        /* Estilo para las pestañas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f8fafc;
            padding: 0.5rem;
            border-radius: 10px;
            border: 1px solid #e5e7eb;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.5rem 1rem;
            border-radius: 8px;
            color: #4b5563;
            font-weight: 500;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #2563eb !important;
            color: white !important;
        }
        
        /* Estilos para las cards de citas */
        .cita-card {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
        }
        
        /* Estilos para los formularios */
        .form-container {
            background-color: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
        }
        
        /* Estilos para los botones */
        .stButton > button {
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        /* Estado de las citas */
        .estado-pendiente {
            background-color: #fef3c7;
            color: #92400e;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-weight: 500;
            font-size: 0.875rem;
        }
        
        .estado-confirmada {
            background-color: #d1fae5;
            color: #065f46;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-weight: 500;
            font-size: 0.875rem;
        }
        
        .estado-finalizada {
            background-color: #dbeafe;
            color: #1e40af;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-weight: 500;
            font-size: 0.875rem;
        }
        
        .estado-cancelada {
            background-color: #fee2e2;
            color: #991b1b;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-weight: 500;
            font-size: 0.875rem;
        }
        
        /* Estilos para los filtros */
        .filtros-container {
            background-color: #f8fafc;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #e5e7eb;
            margin-bottom: 1.5rem;
        }

        /* Estilos para inputs y selects */
        .stSelectbox > div > div {
            border-radius: 8px !important;
        }
        
        .stTextInput > div > div {
            border-radius: 8px !important;
        }

        /* Estilos para el calendario */
        .fc {
            background-color: white;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .fc-toolbar-title {
            color: #1f2937 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("Gestión de Tratamientos 🏥")

    # Crear las pestañas para la navegación
    tabs = st.tabs(["📝Nuevo Tratamiento", "📋Lista de Tratamientos"])

    with tabs[0]:
        show_new_treatment()

    with tabs[1]:
        show_tratamientos_list()

def show_new_treatment():
    """
    Muestra el formulario para registrar un nuevo tratamiento
    """
    st.subheader("📝 Registrar Nuevo Tratamiento")

    st.markdown(
        """
        <style>
        .form-container {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.form("form_nuevo_tratamiento", clear_on_submit=True):
        st.markdown('<div class="form-container">', unsafe_allow_html=True)

        # Nombre del Tratamiento
        nombre_tratamiento = st.text_input(
            "📄 Nombre del Tratamiento",
            placeholder="Introduce el nombre del tratamiento",
        )

        # Descripción
        descripcion = st.text_area(
            "📋 Descripción",
            placeholder="Describe los detalles del tratamiento...",
            height=120,
        )

        # Precio
        precio = st.number_input(
            "💰 Precio (€)",
            min_value=0.0,
            step=0.1,
            help="Introduce el precio del tratamiento en euros.",
        )

        # Estado
        estado = st.selectbox(
            "Estado",
            options=["Activo", "Finalizada", "Cancelada"],
            index=0,
            help="Selecciona el estado actual del tratamiento.",
        )

        # Cliente
        try:
            response = requests.get("http://localhost:8000/clientes/")
            if response.status_code == 200:
                clientes = response.json()
                cliente_opciones = ["Seleccione un cliente"] + [
                    f"{c['nombre_cliente']} (DNI: {c['dni']})" for c in clientes
                ]
                cliente_seleccionado = st.selectbox(
                    "👤 Cliente",
                    options=cliente_opciones,
                    help="Selecciona el cliente asociado al tratamiento.",
                )

                if cliente_seleccionado != "Seleccione un cliente":
                    dni_seleccionado = cliente_seleccionado.split("DNI: ")[1].strip(")")
                    id_cliente = next(
                        c["id_cliente"] for c in clientes if c["dni"] == dni_seleccionado
                    )
                else:
                    id_cliente = None
            else:
                st.error("Error al cargar la lista de clientes")
                id_cliente = None
        except Exception as e:
            st.error(f"Error al cargar clientes: {str(e)}")
            id_cliente = None

        # Botón de envío
        submitted = st.form_submit_button("Registrar Tratamiento")

        if submitted:
            valido, mensaje = validar_tratamiento(
                nombre_tratamiento, descripcion, precio, estado, id_cliente
            )
            if not valido:
                st.error(mensaje)
                return

            try:
                tratamiento_data = {
                    "nombre_tratamiento": nombre_tratamiento,
                    "descripcion": descripcion,
                    "precio": precio,
                    "estado": estado,
                    "id_cliente": id_cliente,
                }

                response = requests.post(
                    "http://localhost:8000/tratamientos/", json=tratamiento_data
                )

                if response.status_code == 201:
                    st.success("¡Tratamiento registrado exitosamente!")
                else:
                    st.error(f"Error al registrar el tratamiento: {response.text}")
            except Exception as e:
                st.error(f"Error al procesar el registro: {str(e)}")

        st.markdown('</div>', unsafe_allow_html=True)



def show_tratamientos_list():
    st.title("📋 Catálogo de Tratamientos")

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        nombre_filtro = st.text_input(
            label="Filtrar por Nombre del Tratamiento",
            key="nombre_filtro",
            placeholder="Nombre del Tratamiento",
            label_visibility="hidden"
        )
    with col2:
        estado_filtro = st.selectbox(
            "Estado",
            ["Todos", "Activo", "Finalizada", "Cancelada"],
            key="estado_filtro"
        )

    precio_min = st.slider(
        "Precio mínimo (€)",
        min_value=0,
        max_value=1000,
        value=0,
        step=50
    )

    try:
        response = requests.get("http://localhost:8000/tratamientos/")
        if response.status_code == 200:
            tratamientos = response.json()
            if tratamientos:
                tratamientos_filtrados = [
                    t for t in tratamientos
                    if (not nombre_filtro or nombre_filtro.lower() in t['nombre_tratamiento'].lower()) and
                    (estado_filtro == "Todos" or t['estado'] == estado_filtro) and
                    (t['precio'] >= precio_min)
                ]

                if not tratamientos_filtrados:
                    st.info("No se encontraron tratamientos con los filtros especificados")
                    return

                for tratamiento in tratamientos_filtrados:
                    with st.container():
                        st.markdown("""
                            <div style="border:1px solid #ddd; border-radius:10px; padding:15px; 
                            margin-bottom:20px; background-color:#f8f9fa; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns([3, 2, 1])

                        with col1:
                            st.markdown(f"### 💊 {tratamiento['nombre_tratamiento']}")
                            st.write(f"📝 **Descripción:** {tratamiento['descripcion']}")

                        with col2:
                            st.write(f"💰 **Precio:** {tratamiento['precio']}€")
                            estado_color = {
                                "Activo": "🟢",
                                "Finalizada": "🔵",
                                "Cancelada": "🔴"
                            }
                            st.write(f"Estado: {estado_color.get(tratamiento['estado'], '⚪')} {tratamiento['estado']}")

                        with col3:
                            if tratamiento['estado'] != 'Finalizada':
                                if st.button("✏️", key=f"edit_{tratamiento['id_tratamiento']}"):
                                    show_edit_form(tratamiento)
                                if st.button("❌", key=f"delete_{tratamiento['id_tratamiento']}"):
                                    if tratamiento['estado'] != 'Cancelada':
                                        delete_treatment(tratamiento['id_tratamiento'])
                                    else:
                                        st.warning("No se pueden eliminar tratamientos cancelados")

                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No hay tratamientos registrados")
        else:
            st.error("Error al cargar los tratamientos")
    except Exception as e:
        st.error(f"Error: {str(e)}")

@st.dialog("Editar Tratamiento")
def show_edit_form(tratamiento):
    with st.form("form_editar_tratamiento"):
        nombre = st.text_input("Nombre", value=tratamiento['nombre_tratamiento'])
        descripcion = st.text_area("Descripción", value=tratamiento['descripcion'])
        precio = st.number_input("Precio (€)", value=float(tratamiento['precio']), min_value=0.0)
        estado = st.selectbox(
            "Estado",
            ["Activo", "Finalizada", "Cancelada"],
            index=["Activo", "Finalizada", "Cancelada"].index(tratamiento['estado'])
        )
        
        submitted = st.form_submit_button("Guardar Cambios")
        if submitted:
            try:
                response = requests.put(
                    f"http://localhost:8000/tratamientos/{tratamiento['id_tratamiento']}",
                    json={
                        "nombre_tratamiento": nombre,
                        "descripcion": descripcion,
                        "precio": precio,
                        "estado": estado
                    }
                )
                
                if response.status_code == 200:
                    st.success("Tratamiento actualizado exitosamente")
                    st.experimental_rerun()
                else:
                    st.error("Error al actualizar el tratamiento")
            except Exception as e:
                st.error(f"Error: {str(e)}")

def delete_treatment(id_tratamiento):
    try:
        response = requests.delete(f"http://localhost:8000/tratamientos/{id_tratamiento}")
        if response.status_code == 200:
            st.success("Tratamiento eliminado exitosamente")
            st.experimental_rerun()
        else:
            st.error("Error al eliminar el tratamiento")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def show_edit_form(tratamiento):
    with st.form("form_editar_tratamiento"):
        nombre = st.text_input("Nombre", value=tratamiento['nombre_tratamiento'])
        descripcion = st.text_area("Descripción", value=tratamiento['descripcion'])
        precio = st.number_input("Precio", value=float(tratamiento['precio']), min_value=0.0)
        estado = st.selectbox(
            "Estado",
            ["Activo", "Finalizada", "Cancelada"],
            index=["Activo", "Finalizada", "Cancelada"].index(tratamiento['estado'])
        )
        
        submitted = st.form_submit_button("Guardar Cambios")
        if submitted:
            try:
                datos_actualizados = {
                    "nombre_tratamiento": nombre,
                    "descripcion": descripcion,
                    "precio": precio,
                    "estado": estado
                }
                
                response = requests.put(
                    f"http://localhost:8000/tratamientos/{tratamiento['id_tratamiento']}",
                    json=datos_actualizados
                )
                
                if response.status_code == 200:
                    st.success("Tratamiento actualizado exitosamente")
                    st.experimental_rerun()
                else:
                    st.error("Error al actualizar el tratamiento")
            except Exception as e:
                st.error(f"Error: {str(e)}")


@st.dialog("Editar Tratamiento")
def show_edit_form(tratamiento):
    """
    Muestra el formulario para editar un tratamiento
    """
    with st.form("form_editar_tratamiento"):
        nombre = st.text_input(
            "Nombre",
            value=tratamiento['nombre_tratamiento']
        )
        descripcion = st.text_area(
            "Descripción",
            value=tratamiento['descripcion']
        )
        precio = st.number_input(
            "Precio (€)",
            value=float(tratamiento['precio']),
            min_value=0.0
        )
        estado = st.selectbox(
            "Estado",
            options=["Activo", "Finalizada", "Cancelada"],
            index=["Activo", "Finalizada", "Cancelada"].index(tratamiento['estado'])
        )
        
        submitted = st.form_submit_button("Guardar Cambios")
        
        if submitted:
            try:
                datos_actualizados = {
                    "nombre_tratamiento": nombre,
                    "descripcion": descripcion,
                    "precio": precio,
                    "estado": estado
                }
                
                response = requests.put(
                    f"http://localhost:8000/tratamientos/{tratamiento['id_tratamiento']}",
                    json=datos_actualizados
                )
                
                if response.status_code == 200:
                    st.success("Tratamiento actualizado exitosamente")
                    st.experimental_rerun()
                else:
                    st.error("Error al actualizar el tratamiento")
            except Exception as e:
                st.error(f"Error: {str(e)}")

def delete_treatment(id_tratamiento):
    """
    Elimina un tratamiento
    """
    try:
        response = requests.delete(
            f"http://localhost:8000/tratamientos/{id_tratamiento}"
        )
        if response.status_code == 200:
            st.success("Tratamiento eliminado exitosamente")
            st.experimental_rerun()
        else:
            st.error("Error al eliminar el tratamiento")
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    show()