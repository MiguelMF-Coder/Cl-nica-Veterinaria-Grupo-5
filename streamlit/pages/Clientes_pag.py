import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
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


    # Inicializar st.session_state.mostrar_mascotas si no existe
    if 'mostrar_mascotas' not in st.session_state:
        st.session_state.mostrar_mascotas = {}

    st.title("Gestión de Clientes 👥")

    # Crear las pestañas para la navegación
    tabs = st.tabs(["📝Nuevo Cliente", "📋Lista de Clientes"])

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


    # Mostrar el formulario dentro de un contenedor con estilo
    with st.container():

        # Título del formulario
        st.markdown('<div class="form-title">📝 Complete la Información del Cliente</div>', unsafe_allow_html=True)

        add_vertical_space(1)

        with st.form("form_nuevo_cliente", clear_on_submit=True):
            col1, col2 = st.columns(2)

            # Columna izquierda
            with col1:
                nombre_cliente = st.text_input("👤 Nombre del Cliente")
                edad = st.number_input("🎂 Edad", min_value=0, max_value=120, step=1)
                dni = st.text_input("🆔 DNI (8 números + letra)")

                # Validación de DNI
                if dni:
                    valido, mensaje = validar_dni(dni)
                    if not valido:
                        st.error(mensaje)

            # Columna derecha
            with col2:
                direccion = st.text_input("📍 Dirección")
                telefono = st.text_input("📞 Teléfono (debe empezar con 6, 7 o 9)")

                # Validación de teléfono
                if telefono:
                    valido, mensaje = validar_telefono(telefono)
                    if not valido:
                        st.error(mensaje)

            add_vertical_space(1)

            # Botón para registrar en el centro
            col1, col2, col3 = st.columns([4.7, 2, 4])
            with col2:
                submitted = st.form_submit_button("Registrar", type="primary")

        st.markdown('</div>', unsafe_allow_html=True)

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

            response = requests.post("http://fastapi:8000/clientes/", json=cliente_data)
            if response.status_code == 201:
                st.success("¡Cliente registrado exitosamente! 🥳")
            else:
                st.error(f"❌ Error al registrar el cliente: {response.text}")
        except Exception as e:
            st.error(f"⚠️ Error al procesar el registro: {str(e)}")



def show_lista_clientes():
    """
    Muestra la lista de clientes con filtros adicionales para mascotas
    """
    # Inicializar st.session_state.mostrar_mascotas si no existe
    if 'mostrar_mascotas' not in st.session_state:
        st.session_state.mostrar_mascotas = {}

    # Inicializar st.session_state.confirmar_eliminacion y cliente_a_eliminar si no existen
    if 'confirmar_eliminacion' not in st.session_state:
        st.session_state.confirmar_eliminacion = False
    if 'cliente_a_eliminar' not in st.session_state:
        st.session_state.cliente_a_eliminar = None

    st.title("📋 Lista de Clientes")

    # Filtros en dos filas
    col1, col2 = st.columns(2)
    with col1:
        nombre_filtro = st.text_input(
            label="Filtrar por Nombre del Cliente",
            key="nombre_filtro",
            placeholder="Nombre del Cliente",
            label_visibility="hidden"
        )
    with col2:
        dni_filtro = st.text_input(
            label="Filtrar por DNI del Cliente",
            key="dni_filtro",
            placeholder="DNI del Cliente",
            label_visibility="hidden"
        )

    col3, col4 = st.columns(2)
    with col3:
        mascota_filtro = st.text_input(
            label="Filtrar por Nombre de la Mascota",
            key="mascota_filtro",
            placeholder="Nombre de la Mascota",
            label_visibility="hidden"
        )
    with col4:
        raza_filtro = st.text_input(
            label="Filtrar por Raza de la Mascota",
            key="raza_filtro",
            placeholder="Raza de la Mascota",
            label_visibility="hidden"
        )

    try:
        # Obtener todos los clientes
        response = requests.get("http://fastapi:8000/clientes/")
        if response.status_code == 200:
            clientes = response.json()
            if clientes:
                # Lista para almacenar los IDs de clientes que coinciden con los filtros de mascota
                clientes_filtrados_ids = set()
                
                # Si hay filtros de mascota, buscar primero las mascotas que coinciden
                if mascota_filtro or raza_filtro:
                    for cliente in clientes:
                        try:
                            mascotas_response = requests.get(
                                f"http://fastapi:8000/mascotas/cliente/{cliente['id_cliente']}"
                            )
                            if mascotas_response.status_code == 200:
                                mascotas = mascotas_response.json()
                                for mascota in mascotas:
                                    if (mascota_filtro.lower() in mascota['nombre_mascota'].lower() or not mascota_filtro) and \
                                       (raza_filtro.lower() in mascota['raza'].lower() or not raza_filtro):
                                        clientes_filtrados_ids.add(cliente['id_cliente'])
                        except Exception as e:
                            logger.error(f"Error al obtener mascotas del cliente {cliente['id_cliente']}: {str(e)}")
                            st.error(f"Error al obtener mascotas del cliente {cliente['id_cliente']}")
                clientes_filtrados = []
                for cliente in clientes:
                    if nombre_filtro and nombre_filtro.lower() not in cliente['nombre_cliente'].lower():
                        continue
                    if dni_filtro and dni_filtro.lower() not in cliente['dni'].lower():
                        continue
                    if (mascota_filtro or raza_filtro) and cliente['id_cliente'] not in clientes_filtrados_ids:
                        continue
                    clientes_filtrados.append(cliente)
                
                if not clientes_filtrados:
                    st.info("No se encontraron clientes con los filtros especificados")
                    return
                
                for cliente in clientes_filtrados:
                    st.markdown("""
                        <style>
                            .cliente-card {
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
                        st.markdown('<div class="cliente-card">', unsafe_allow_html=True)

                        # Información principal del cliente
                        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                        
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
                                    st.session_state.confirmar_eliminacion = True
                                    st.session_state.cliente_a_eliminar = cliente

                        with col4:
                            # Botón para mostrar/ocultar mascotas
                            if st.button("🐾", key=f"mascotas_{cliente['id_cliente']}"):
                                if cliente['id_cliente'] in st.session_state.mostrar_mascotas:
                                    st.session_state.mostrar_mascotas.pop(cliente['id_cliente'])
                                else:
                                    st.session_state.mostrar_mascotas[cliente['id_cliente']] = True

                        # Mostrar sección de mascotas si está expandida
                        if cliente['id_cliente'] in st.session_state.mostrar_mascotas:
                            with st.container():
                                st.markdown("#### 🐾 Mascotas")
                                mostrar_mascotas(cliente['id_cliente'])
                                # Botón para añadir nueva mascota
                                if st.button("➕ Añadir Mascota", key=f"add_mascota_{cliente['id_cliente']}"):
                                    show_add_mascota_form(cliente['id_cliente'])

                                try:
                                    mascotas_response = requests.get(
                                        f"http://fastapi:8000/mascotas/cliente/{cliente['id_cliente']}"
                                    )
                                    if mascotas_response.status_code == 200:
                                        mascotas = mascotas_response.json()
                                        for mascota in mascotas:
                                            if (mascota_filtro.lower() in mascota['nombre_mascota'].lower() or not mascota_filtro) and \
                                               (raza_filtro.lower() in mascota['raza'].lower() or not raza_filtro):
                                                clientes_filtrados_ids.add(cliente['id_cliente'])
                                except Exception as e:
                                    logger.error(f"Error al obtener mascotas del cliente {cliente['id_cliente']}: {str(e)}")
                                    st.error(f"Error al obtener mascotas del cliente {cliente['id_cliente']}")

                        # Confirmación de eliminación de cliente
                        if (st.session_state.confirmar_eliminacion and 
                            st.session_state.cliente_a_eliminar and 
                            st.session_state.cliente_a_eliminar['id_cliente'] == cliente['id_cliente']):
                            
                            st.warning(f"¿Está seguro de eliminar al cliente {cliente['nombre_cliente']}?")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Sí", key=f"confirm_yes_{cliente['id_cliente']}"):
                                    try:
                                        response = requests.delete(
                                            f"http://fastapi:8000/clientes/{cliente['id_cliente']}"
                                        )
                                        if response.status_code == 200:
                                            st.success("Cliente eliminado exitosamente")
                                            st.session_state.confirmar_eliminacion = False
                                            st.session_state.cliente_a_eliminar = None
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"Error al eliminar el cliente: {str(e)}")
                            with col2:
                                if st.button("No", key=f"confirm_no_{cliente['id_cliente']}"):
                                    st.session_state.confirmar_eliminacion = False
                                    st.session_state.cliente_a_eliminar = None
                                    st.rerun()
            else:
                st.info("No hay clientes registrados")
        else:
            st.error("Error al cargar la lista de clientes")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def mostrar_mascotas(cliente_id):
    """
    Muestra las mascotas de un cliente.
    """
    try:
        mascotas_response = requests.get(f"http://fastapi:8000/mascotas/cliente/{cliente_id}")
        if mascotas_response.status_code == 200:
            mascotas = mascotas_response.json()
            if mascotas:
                for mascota in mascotas:
                    st.markdown("""
                        <style>
                        .mascota-container {
                            border: 1px solid #ddd;
                            border-radius: 10px;
                            padding: 15px;
                            margin: 10px 0;
                            background-color: #f8f9fa;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    with st.container():
                        st.markdown('<div class="mascota-container">', unsafe_allow_html=True)
                        mcol1, mcol2, mcol3 = st.columns([3, 2, 1])
                        
                        with mcol1:
                            st.write(f"🐕 **Nombre:** {mascota['nombre_mascota']}")
                            st.write(f"🔍 **Raza:** {mascota['raza']}")
                        
                        with mcol2:
                            st.write(f"🎂 **Edad:** {mascota['edad']}")
                            st.write(f"🏥 **Estado:** {mascota['estado']}")
                        
                        with mcol3:
                            if st.button("✏️", key=f"edit_mascota_{mascota['id_mascota']}"):
                                show_edit_mascota_form(mascota)
                            if st.button("❌", key=f"delete_mascota_{mascota['id_mascota']}"):
                                delete_mascota(mascota['id_mascota'])
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Este cliente no tiene mascotas registradas")
        else:
            st.error("Error al cargar las mascotas")
    except Exception as e:
        st.error(f"Error al cargar las mascotas: {str(e)}")


@st.dialog("Añadir Mascota")
def show_add_mascota_form(id_cliente):
    """
    Formulario para añadir una nueva mascota
    """
    with st.form("form_nueva_mascota"):
        nombre = st.text_input("Nombre de la Mascota")
        raza = st.text_input("Raza")
        edad = st.number_input("Edad", min_value=0, max_value=50)
        afeccion = st.text_input("Afección (opcional)")
        estado = st.selectbox("Estado", ["Vivo", "Fallecido"])
        
        submitted = st.form_submit_button("Guardar Mascota")
        if submitted:
            if not all([nombre, raza, edad is not None]):
                st.error("Por favor complete todos los campos obligatorios")
                return

            mascota_data = {
                "nombre_mascota": nombre,
                "raza": raza,
                "edad": edad,
                "afeccion": afeccion,
                "estado": estado,
                "id_cliente": id_cliente
            }

            try:
                response = requests.post(
                    "http://fastapi:8000/mascotas/",
                    json=mascota_data
                )
                if response.status_code == 201:
                    st.success("Mascota registrada exitosamente")
                    st.rerun()
                else:
                    st.error("Error al registrar la mascota")
            except Exception as e:
                st.error(f"Error al registrar la mascota: {str(e)}")

@st.dialog("Editar Mascota")
def show_edit_mascota_form(mascota):
    """
    Formulario para editar una mascota existente
    """
    with st.form("form_editar_mascota"):
        nombre = st.text_input("Nombre de la Mascota", value=mascota['nombre_mascota'])
        raza = st.text_input("Raza", value=mascota['raza'])
        edad = st.number_input("Edad", min_value=0, max_value=50, value=mascota['edad'])
        afeccion = st.text_input("Afección", value=mascota.get('afeccion', ''))
        estado = st.selectbox("Estado", ["Vivo", "Fallecido"], index=0 if mascota['estado'] == "Vivo" else 1)
        
        submitted = st.form_submit_button("Guardar Cambios")
        if submitted:
            mascota_actualizada = {
                "nombre_mascota": nombre,
                "raza": raza,
                "edad": edad,
                "afeccion": afeccion,
                "estado": estado
            }
            
            try:
                response = requests.put(
                    f"http://fastapi:8000/mascotas/{mascota['id_mascota']}",
                    json=mascota_actualizada
                )
                if response.status_code == 200:
                    st.success("Mascota actualizada exitosamente")
                    st.rerun()
                else:
                    st.error("Error al actualizar la mascota")
            except Exception as e:
                st.error(f"Error al actualizar la mascota: {str(e)}")

def delete_mascota(id_mascota):
    """
    Elimina una mascota
    """
    try:
        response = requests.delete(f"http://fastapi:8000/mascotas/{id_mascota}")
        if response.status_code == 200:
            st.success("Mascota eliminada exitosamente")
            st.rerun()
        else:
            st.error("Error al eliminar la mascota")
    except Exception as e:
        st.error(f"Error al eliminar la mascota: {str(e)}")

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
                f"http://fastapi:8000/clientes/{cliente['id_cliente']}", 
                json=cliente_actualizado
            )
            
            if response.status_code == 200:
                st.success("Cliente actualizado exitosamente")
                st.rerun()
            else:
                st.error("Error al actualizar el cliente")

def delete_cliente(id_cliente):
    """
    Elimina un cliente
    """
    try:
        response = requests.delete(f"http://fastapi:8000/clientes/{id_cliente}")
        if response.status_code == 200:
            st.success("Cliente eliminado exitosamente")
            st.rerun()
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
                response = requests.get(f"http://fastapi:8000/clientes/buscar", params={"dni": dni_buscar})
            elif nombre_buscar:
                response = requests.get(f"http://fastapi:8000/clientes/buscar", params={"nombre": nombre_buscar})
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

def cargar_y_filtrar_clientes(nombre_filtro="", dni_filtro="", mascota_filtro="", raza_filtro=""):
    """
    Carga y filtra la lista de clientes según los criterios especificados
    """
    try:
        # Obtener todos los clientes
        response = requests.get("http://fastapi:8000/clientes/")
        if response.status_code != 200:
            st.error("Error al cargar la lista de clientes")
            return []

        clientes = response.json()
        if not clientes:
            return []

        # Si hay filtros de mascota, obtener las mascotas que coinciden
        clientes_filtrados_ids = set()
        if mascota_filtro or raza_filtro:
            mascotas_response = requests.get(
                "http://fastapi:8000/mascotas/buscar",
                params={
                    "nombre": mascota_filtro if mascota_filtro else None,
                    "raza": raza_filtro if raza_filtro else None
                }
            )
            
            if mascotas_response.status_code == 200:
                mascotas = mascotas_response.json()
                clientes_filtrados_ids = {mascota['id_cliente'] for mascota in mascotas}

        # Aplicar filtros de cliente
        return [
            cliente for cliente in clientes
            if (not nombre_filtro or nombre_filtro.lower() in cliente['nombre_cliente'].lower()) and
               (not dni_filtro or dni_filtro.lower() in cliente['dni'].lower()) and
               (not (mascota_filtro or raza_filtro) or cliente['id_cliente'] in clientes_filtrados_ids)
        ]
    except Exception as e:
        logger.error(f"Error al cargar y filtrar clientes: {str(e)}")
        st.error(f"Error al cargar los datos: {str(e)}")
        return []

if __name__ == "__main__":
    show()