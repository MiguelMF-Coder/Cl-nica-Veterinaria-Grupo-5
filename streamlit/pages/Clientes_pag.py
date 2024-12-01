import streamlit as st
import pandas as pd
from datetime import datetime
import requests
import logging
import json

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def show():
    st.title("Gestión de Clientes 👥")

    # Crear las pestañas para la navegación
    tabs = st.tabs(["Nuevo Cliente", "Lista de Clientes"])

    with tabs[0]:
        show_nuevo_cliente()

    with tabs[1]:
        show_lista_clientes()


def validar_dni(dni):
    """Valida el formato del DNI (8 números + 1 letra)"""
    if len(dni) != 9:
        return False, "El DNI debe tener 9 caracteres"
    if not dni[:8].isdigit():
        return False, "Los primeros 8 caracteres deben ser números"
    if not dni[8].isalpha():
        return False, "El último carácter debe ser una letra"
    return True, ""

def validar_telefono(telefono):
    """Valida el formato del teléfono"""
    if len(telefono) != 9:
        return False, "El teléfono debe tener 9 dígitos"
    if not telefono.isdigit():
        return False, "El teléfono debe contener solo números"
    if not telefono[0] in ['6', '7', '9']:
        return False, "El teléfono debe empezar por 6, 7 o 9"
    return True, ""

def show_nuevo_cliente():
    """
    Muestra el formulario para registrar un nuevo cliente
    """
    st.subheader("📝 Registrar Nuevo Cliente")

    with st.form("form_nuevo_cliente", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            nombre_cliente = st.text_input("Nombre del Cliente")
            edad = st.number_input("Edad", min_value=0, max_value=120, step=1)
            dni = st.text_input("DNI (8 números + letra)")
            
            # Validación de DNI
            if dni:
                valido, mensaje = validar_dni(dni)
                if not valido:
                    st.error(mensaje)
        
        with col2:
            direccion = st.text_input("Dirección")
            telefono = st.text_input("Teléfono (debe empezar con 6, 7 o 9)")
            
            # Validación de teléfono
            if telefono:
                valido, mensaje = validar_telefono(telefono)
                if not valido:
                    st.error(mensaje)

        # Botón centrado
        col1, col2, col3 = st.columns([4.7, 2, 4])
        with col2:
            submitted = st.form_submit_button("Registrar")

        if submitted:
            if not all([nombre_cliente, edad, dni, direccion, telefono]):
                st.error("Por favor, complete todos los campos obligatorios")
                return

            # Validar longitudes de campos
            if len(nombre_cliente) > 100:
                st.error("El nombre no debe exceder los 100 caracteres")
                return
            if len(direccion) > 200:
                st.error("La dirección no debe exceder los 200 caracteres")
                return

            # Validar DNI y teléfono
            dni_valido, dni_mensaje = validar_dni(dni)
            telefono_valido, telefono_mensaje = validar_telefono(telefono)

            if not dni_valido:
                st.error(dni_mensaje)
                return
            if not telefono_valido:
                st.error(telefono_mensaje)
                return

            try:
                cliente_data = {
                    "nombre_cliente": nombre_cliente,
                    "edad": edad,
                    "dni": dni.upper(),
                    "direccion": direccion,
                    "telefono": telefono
                }

                response = requests.post("http://localhost:8000/clientes/", json=cliente_data)
                if response.status_code == 201:
                    st.success("¡Cliente registrado exitosamente!")
                else:
                    st.error(f"Error al registrar el cliente: {response.text}")
            except Exception as e:
                st.error(f"Error al procesar el registro: {str(e)}")

def show_lista_clientes():
    """
    Muestra la lista de clientes con formato similar a la lista de citas
    """
    st.subheader("📋 Lista de Clientes")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        nombre_filtro = st.text_input("Filtrar por Nombre")
    with col2:
        dni_filtro = st.text_input("Filtrar por DNI")

    try:
        response = requests.get("http://localhost:8000/clientes/")
        if response.status_code == 200:
            clientes = response.json()
            if clientes:
                # Aplicar filtros si existen
                if nombre_filtro:
                    clientes = [c for c in clientes if nombre_filtro.lower() in c['nombre_cliente'].lower()]
                if dni_filtro:
                    clientes = [c for c in clientes if dni_filtro.lower() in c['dni'].lower()]
                
                # Mostrar clientes
                for cliente in clientes:
                    with st.container():
                        col1, col2, col3 = st.columns([3,2,1])
                        
                        with col1:
                            st.markdown(f"### 👤 {cliente['nombre_cliente']}")
                            st.write(f"📝 **DNI:** {cliente['dni']}")
                        
                        with col2:
                            st.write(f"📞 **Teléfono:** {cliente['telefono']}")
                            st.write(f"📍 **Dirección:** {cliente['direccion']}")
                            st.write(f"🎂 **Edad:** {cliente['edad']}")
                            
                        with col3:
                            col_edit, col_delete = st.columns(2)
                            with col_edit:
                                if st.button("✏️", key=f"edit_{cliente['id_cliente']}"):
                                    show_edit_form(cliente)
                            with col_delete:
                                if st.button("❌", key=f"delete_{cliente['id_cliente']}"):
                                    if st.warning(f"¿Está seguro de eliminar al cliente {cliente['nombre_cliente']}?"):
                                        delete_cliente(cliente['id_cliente'])
                        
                        st.markdown("---")
            else:
                st.info("No hay clientes registrados")
        else:
            st.error("Error al cargar la lista de clientes")
    except Exception as e:
        st.error(f"Error: {str(e)}")

@st.dialog("Editar Cliente")
def show_edit_form(cliente):
    """
    Muestra un formulario para editar un cliente
    """
    with st.form("form_editar_cliente"):
        nombre = st.text_input("Nombre del Cliente", value=cliente['nombre_cliente'])
        edad = st.number_input("Edad", value=cliente['edad'], min_value=0, max_value=120)
        dni = st.text_input("DNI", value=cliente['dni'])
        direccion = st.text_input("Dirección", value=cliente['direccion'])
        telefono = st.text_input("Teléfono", value=cliente['telefono'])
        
        submitted = st.form_submit_button("Guardar Cambios")
        if submitted:
            # Validaciones
            dni_valido, dni_mensaje = validar_dni(dni)
            telefono_valido, telefono_mensaje = validar_telefono(telefono)

            if not dni_valido:
                st.error(dni_mensaje)
                return
            if not telefono_valido:
                st.error(telefono_mensaje)
                return

            cliente_actualizado = {
                "nombre_cliente": nombre,
                "edad": edad,
                "dni": dni.upper(),
                "direccion": direccion,
                "telefono": telefono
            }
            
            response = requests.put(
                f"http://localhost:8000/clientes/{cliente['id_cliente']}", 
                json=cliente_actualizado
            )
            
            if response.status_code == 200:
                st.success("Cliente actualizado exitosamente")
                st.experimental_rerun()
            else:
                st.error("Error al actualizar el cliente")

def delete_cliente(id_cliente):
    """
    Elimina un cliente
    """
    try:
        response = requests.delete(f"http://localhost:8000/clientes/{id_cliente}")
        if response.status_code == 200:
            st.success("Cliente eliminado exitosamente")
            st.experimental_rerun()
        else:
            st.error("Error al eliminar el cliente")
    except Exception as e:
        st.error(f"Error al eliminar el cliente: {str(e)}")

def show_buscar_cliente():
    """
    Muestra la interfaz de búsqueda de clientes
    """
    st.subheader("🔍 Buscar Cliente")

    col1, col2 = st.columns(2)
    
    with col1:
        dni_buscar = st.text_input("Buscar por DNI")
    with col2:
        nombre_buscar = st.text_input("Buscar por Nombre")

    if st.button("Buscar"):
        try:
            if dni_buscar:
                response = requests.get(f"http://localhost:8000/clientes/buscar", params={"dni": dni_buscar})
            elif nombre_buscar:
                response = requests.get(f"http://localhost:8000/clientes/buscar", params={"nombre": nombre_buscar})
            else:
                st.warning("Por favor, ingrese un DNI o nombre para buscar")
                return

            if response.status_code == 200:
                clientes = response.json()
                if clientes:
                    for cliente in clientes:
                        with st.container():
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Nombre:** {cliente['nombre_cliente']}")
                                st.write(f"**DNI:** {cliente['dni']}")
                                st.write(f"**Edad:** {cliente['edad']}")
                            with col2:
                                st.write(f"**Teléfono:** {cliente['telefono']}")
                                st.write(f"**Dirección:** {cliente['direccion']}")
                            st.markdown("---")
                else:
                    st.info("No se encontraron clientes con esos criterios")
            else:
                st.error("Error al buscar el cliente")
        except Exception as e:
            st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    show()