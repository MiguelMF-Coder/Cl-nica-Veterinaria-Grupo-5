import streamlit as st
import importlib
import sys
from pathlib import Path
import logging
import requests

# Configuración de la aplicación
st.set_page_config(page_title="Clínica Veterinaria", layout="wide", page_icon="🐾")

# Configuración del logging
def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("streamlit_app.log")
        ]
    )
setup_logger()
logger = logging.getLogger(__name__)
logger.info("Iniciando la aplicación...")

# Configuración de rutas
pages_path = Path(__file__).parent / "streamlit/pages"
if pages_path.exists() and pages_path.is_dir():
    sys.path.append(str(pages_path))
    logger.info(f"Ruta de páginas añadida a sys.path: {pages_path}")
else:
    logger.error(f"La carpeta de páginas {pages_path} no existe o no es un directorio.")
    st.error(f"Error: La carpeta de páginas no existe o no es válida. Verifique la estructura de archivos.")

# Configuración de estilo CSS
st.markdown("""
<style>
    /* Ajuste del logo en la barra lateral */
    [data-testid="stSidebar"] .stImage img {
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 2px solid #e5e7eb;
    }

    /* Ajustes para la barra lateral */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
        border-right: 1px solid #e5e7eb;
    }

    /* Título del menú */
    .sidebar-title {
        text-align: center;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: #374151 !important;
        margin: 0 0 1.5rem 0 !important;
        padding: 0.5rem 1rem !important;
        background: #f3f4f6;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }

    /* Radio buttons en la navegación */
    .stRadio > div[role="radiogroup"] {
        border-radius: 10px;
        background: white;
        padding: 0.5rem;
        border: 1px solid #e5e7eb;
    }

    .stRadio > div[role="radiogroup"] label {
        padding: 0.75rem 1rem !important;
        background: white !important;
        border-radius: 8px !important;
        color: #4b5563 !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        border: 1px solid transparent !important;
        margin: 0.25rem 0 !important;
    }

    .stRadio > div[role="radiogroup"] label:hover {
        background: #f8fafc !important;
        color: #2563eb !important;
        border-color: #93c5fd !important;
        transform: translateX(3px);
    }

    /* Estilo para el botón seleccionado */
    .stRadio > div[role="radiogroup"] label[data-checked="true"] {
        background: #2563eb !important;
        color: white !important;
        border-color: #2563eb !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
    }


    /* Contenedor del botón de cerrar */
    .close-button-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1rem;
        background: linear-gradient(0deg, #f8f9fa 0%, transparent 100%);
        border-top: 1px solid #e5e7eb;
    }

    /* Botón de cerrar ajustado al tamaño de la barra lateral */
    .close-button .stButton > button {
        width: 90% !important; 
        background: linear-gradient(180deg, #ef4444 0%, #dc2626 100%) !important;
        color: white !important;
        padding: 0.75rem !important; /* Espaciado interno para el botón */
        font-weight: 600 !important; /* Texto más visible */
        font-size: 1rem !important; /* Tamaño de fuente del texto */
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2) !important;
        transition: all 0.2s ease !important;
        display: block;
        margin: 0 auto !important; /* Centra el botón horizontalmente */
        text-align: center;
    }

    /* Estilo para hover */
    .close-button .stButton > button:hover {
        background: linear-gradient(180deg, #dc2626 0%, #b91c1c 100%) !important;
        box-shadow: 0 4px 6px rgba(239, 68, 68, 0.3) !important;
        transform: translateY(-1px);
    }


    /* Mensajes de estado */
    .stSuccess, .stError {
        padding: 0.75rem !important;
        border-radius: 8px !important;
        margin-top: 0.5rem !important;
        border: 1px solid;
    }

    .stSuccess {
        background-color: #ecfdf5 !important;
        border-color: #6ee7b7 !important;
    }

    .stError {
        background-color: #fef2f2 !important;
        border-color: #fca5a5 !important;
    }

    /* Ajuste general del contenedor principal */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Diccionario de páginas
pages = {
    "🏠 Inicio": "Inicio",
    "📊 Dashboard": "Dashboard_pag",
    "📅 Citas": "Citas_pag",
    "👥 Clientes": "Clientes_pag",
    "🐕 Mascotas": "Mascotas_pag",
    "💉 Tratamientos": "Tratamientos_pag"
}

# Logo
try:
    st.sidebar.image('streamlit/logo.jpg', use_container_width=True)
except FileNotFoundError:
    logger.warning("El archivo del logo no se encuentra en la ruta especificada.")
    st.sidebar.warning("No se pudo cargar el logo. Verifique que el archivo 'logo.jpg' existe en la carpeta 'streamlit'.")
except Exception as e:
    logger.error(f"Error al cargar el logo: {e}")
    st.sidebar.error(f"Error al cargar el logo: {e}")

# Menú de navegación
st.sidebar.markdown('<p class="sidebar-title">MENÚ PRINCIPAL</p>', unsafe_allow_html=True)
selected_page = st.sidebar.radio("", list(pages.keys()), label_visibility="collapsed")

# Botón de cerrar aplicación
with st.sidebar:
    st.markdown('<div class="close-button-container">', unsafe_allow_html=True)
    st.markdown('<div class="close-button">', unsafe_allow_html=True)
    if st.button("🚪 CERRAR APLICACIÓN"):
        try:
            response = requests.post("http://localhost:8000/api/exportar_todos_json", timeout=10)
            if response.status_code == 200:
                st.success("✅ Datos exportados con éxito")
            else:
                st.error("❌ Error al exportar datos")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    st.markdown('</div></div>', unsafe_allow_html=True)

# Cargar la página seleccionada
if selected_page:
    page_module = pages[selected_page]
    logger.info(f"Intentando cargar la página: {selected_page} (módulo: {page_module})")
    try:
        module = importlib.import_module(page_module)
        if hasattr(module, "show") and callable(getattr(module, "show")):
            logger.info(f"Mostrando página: {selected_page}")
            module.show()
        else:
            logger.error(f"La página {selected_page} no tiene una función `show()`. Por favor, añádala.")
            st.error(f"La página {selected_page} no tiene una función `show()`. Por favor, contacte al administrador.")
    except ModuleNotFoundError as e:
        logger.error(f"No se pudo cargar la página {selected_page}: {e}")
        st.error(f"No se pudo cargar la página: {selected_page}. Módulo no encontrado.")
    except ImportError as e:
        logger.error(f"Error de importación al cargar la página {selected_page}: {e}")
        st.error(f"Error de importación al cargar la página: {e}")
    except Exception as e:
        logger.exception(f"Error inesperado al cargar la página {selected_page}: {e}")
        st.error(f"Ocurrió un error al cargar la página: {e}")