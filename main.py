import streamlit as st
import importlib
import sys
from pathlib import Path

# Agregar la carpeta 'streamlit/pages' al sys.path para que Python pueda importar módulos desde allí
sys.path.append(str(Path(__file__).parent / "streamlit/pages"))

# Configuración de la aplicación
st.set_page_config(page_title="Clínica Veterinaria", layout="wide", page_icon="🐾")

# Logo
st.sidebar.image('streamlit/logo.jpg', use_column_width=True)

# Diccionario de páginas
pages = {
    "Inicio": "Inicio",
    "Dashboard": "Dashboard",
    "Formulario": "Formulario",
    "Calendario": "Calendario",
    "Clientes": "gestion_clientes",
    "Tratamientos": "gestion_tratamientos"
}

# Mostrar los botones en la barra lateral para la navegación
st.sidebar.title("MENÚ")
selected_page = st.sidebar.radio("Selecciona una página", list(pages.keys()))

# Cargar y ejecutar la página seleccionada
if selected_page:
    page_module = pages[selected_page]
    try:
        module = importlib.import_module(page_module)
        # Asume que cada página tiene una función `show()` para mostrar el contenido
        if hasattr(module, "show"):
            module.show()
        else:
            st.error(f"La página {selected_page} no tiene una función `show()`.")
    except ModuleNotFoundError:
        st.error(f"No se pudo cargar la página: {selected_page}")
    except Exception as e:
        st.error(f"Ocurrió un error al cargar la página: {e}")
