import streamlit as st
import importlib
import sys
from pathlib import Path
import logging
import requests

# Configuración del logging para la depuración
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

# Agregar la carpeta 'streamlit/pages' al sys.path para que Python pueda importar módulos desde allí
pages_path = Path(__file__).parent / "streamlit/pages"
if pages_path.exists() and pages_path.is_dir():
    sys.path.append(str(pages_path))
    logger.info(f"Ruta de páginas añadida a sys.path: {pages_path}")
else:
    logger.error(f"La carpeta de páginas {pages_path} no existe o no es un directorio.")
    st.error(f"Error: La carpeta de páginas no existe o no es válida. Verifique la estructura de archivos.")

# Configuración de la aplicación
try:
    st.set_page_config(page_title="Clínica Veterinaria", layout="wide", page_icon="🐾")
except Exception as e:
    logger.error(f"Error al configurar la página: {e}")
    st.error(f"Error al configurar la página: {e}")

# Logo
try:
    st.sidebar.image('streamlit/logo.jpg', use_container_width=True)
except FileNotFoundError:
    logger.warning("El archivo del logo no se encuentra en la ruta especificada.")
    st.sidebar.warning("No se pudo cargar el logo. Verifique que el archivo 'logo.jpg' existe en la carpeta 'streamlit'.")
except Exception as e:
    logger.error(f"Error al cargar el logo: {e}")
    st.sidebar.error(f"Error al cargar el logo: {e}")

# Diccionario de páginas
pages = {
    "Inicio": "Inicio",
    "Dashboard": "Dashboard_pag",
    "Formulario": "Formulario_pag",
    "Citas": "Citas_pag",
    "Clientes": "Clientes_pag",
    "Tratamientos": "Tratamientos_pag",
}

# Mostrar los botones en la barra lateral para la navegación
st.sidebar.title("MENÚ")
selected_page = st.sidebar.radio("Selecciona una página", list(pages.keys()))

# Botón de exportación de datos a JSON
if st.sidebar.button("CERRAR APLICACIÓN"):
    try:
        response = requests.post("http://localhost:8000/api/exportar_todos_json")
        if response.status_code == 200:
            st.sidebar.success("Datos exportados con éxito a JSON.")
            logger.info("Datos exportados con éxito a JSON.")
        else:
            st.sidebar.error(f"Error al exportar los datos: {response.status_code}")
            logger.error(f"Error al exportar los datos: {response.status_code}")
    except Exception as e:
        st.sidebar.error(f"Error al conectar con la API: {str(e)}")
        logger.error(f"Error al conectar con la API para exportar los datos: {str(e)}")

# Cargar y ejecutar la página seleccionada
if selected_page:
    page_module = pages[selected_page]
    logger.info(f"Intentando cargar la página: {selected_page} (módulo: {page_module})")
    try:
        module = importlib.import_module(page_module)
        # Asume que cada página tiene una función `show()` para mostrar el contenido
        if hasattr(module, "show"):
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
    except RuntimeError as e:
        if "numpy.dtype size changed" in str(e):
            logger.error(f"Error de compatibilidad binaria al cargar la página {selected_page}: {e}")
            st.error(f"Error de compatibilidad binaria al cargar la página: {e}. Esto puede indicar una incompatibilidad binaria. Por favor, reinstale numpy.")
        else:
            logger.exception(f"Error inesperado al cargar la página {selected_page}: {e}")
            st.error(f"Ocurrió un error al cargar la página: {e}")
    except Exception as e:
        logger.exception(f"Error inesperado al cargar la página {selected_page}: {e}")
        st.error(f"Ocurrió un error al cargar la página: {e}")
