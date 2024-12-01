import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
from datetime import datetime, timedelta
import requests
import json

def show():
    st.title("Gestión de Citas Veterinarias 📆")

    # Crear las pestañas para la navegación
    tabs = st.tabs(["Calendario de Citas", "Nueva Cita", "Lista de Citas", "Buscar Citas"])

    with tabs[0]:
        show_calendar()

    with tabs[1]:
        show_nueva_cita()

    with tabs[2]:
        show_citas_list()
        
    with tabs[3]:
        show_buscar_citas()

def show_calendar():
    """
    Muestra el calendario interactivo con las citas programadas
    """
    def cargar_citas():
        try:
            response = requests.get("http://localhost:8000/citas/")
            if response.status_code == 200:
                citas = response.json()
                eventos = []
                for cita in citas:
                    colores = {
                        "Pendiente": "#FFBD45",
                        "Confirmada": "#3DD56D",
                        "Finalizada": "#3D9DF3",
                        "Cancelada": "#FF4B4B"
                    }
                    
                    fecha_inicio = datetime.fromisoformat(cita['fecha'])
                    fecha_fin = fecha_inicio + timedelta(hours=1)
                    
                    evento = {
                        "title": f"{cita['descripcion']}",
                        "color": colores.get(cita['estado'], "#FF6C6C"),
                        "start": fecha_inicio.isoformat(),
                        "end": fecha_fin.isoformat(),
                        "resourceId": f"consulta_{cita['id_mascota'] % 3}",
                        "extendedProps": {
                            "id_cita": cita['id_cita'],
                            "cliente": cita.get('cliente', ''),
                            "mascota": cita.get('mascota', ''),
                            "estado": cita['estado']
                        }
                    }
                    eventos.append(evento)
                return eventos
            else:
                st.error(f"Error al cargar citas: {response.status_code}")
                return []
        except Exception as e:
            st.error(f"Error al cargar citas: {str(e)}")
            return []

    calendar_resources = [
        {"id": "consulta_0", "building": "Clínica Principal", "title": "Consulta A"},
        {"id": "consulta_1", "building": "Clínica Principal", "title": "Consulta B"},
        {"id": "consulta_2", "building": "Clínica Principal", "title": "Consulta C"},
    ]

    calendar_options = {
        "editable": "true",
        "navLinks": "true",
        "resources": calendar_resources,
        "selectable": "true",
        "slotMinTime": "08:00:00",
        "slotMaxTime": "20:00:00",
        "initialView": "resourceTimeGridDay",
        "resourceGroupField": "building"
    }

    events = cargar_citas()
    state = calendar(
        events=st.session_state.get("events", events),
        options=calendar_options,
        custom_css="""
        .fc-event-past { opacity: 0.8; }
        .fc-event-time { font-style: italic; }
        .fc-event-title { font-weight: 700; }
        .fc-toolbar-title { font-size: 2rem; }
        """,
        key='calendar'
    )

    if state.get("eventsSet") is not None:
        st.session_state["events"] = state["eventsSet"]

    if state.get('select') is not None:
        st.session_state["time_inicial"] = datetime.fromisoformat(state["select"]["start"])
        st.session_state["time_final"] = datetime.fromisoformat(state["select"]["end"])
        st.switch_page("Nueva Cita")  # Cambiar a la pestaña de nueva cita

def show_nueva_cita():
    """
    Formulario de nueva cita
    """
    st.title("Nueva Cita 📝")

    with st.form("form_nueva_cita", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📅 Detalles de la Cita")
            
            # Fecha
            fecha = st.date_input(
                "Fecha",
                min_value=datetime.today(),
                format="DD/MM/YYYY"
            )
            
            # Hora
            hora = st.time_input(
                "Hora",
                datetime.now().time()
            )
                        
            # Cliente
            try:
                response = requests.get("http://localhost:8000/clientes/")
                if response.status_code == 200:
                    clientes = response.json()
                    cliente_nombres = ["Seleccione un cliente"] + [
                        f"{c['nombre_cliente']} (DNI: {c['dni']})" 
                        for c in clientes
                    ]
                    cliente_seleccionado = st.selectbox(
                        "Cliente",
                        options=cliente_nombres,
                        key="cliente_select"
                    )

                    # Mascota
                    if cliente_seleccionado != "Seleccione un cliente":
                        dni_seleccionado = cliente_seleccionado.split("DNI: ")[1].strip(")")
                        client_id = next(c['id_cliente'] for c in clientes if c['dni'] == dni_seleccionado)
                        
                        response = requests.get(f"http://localhost:8000/mascotas/cliente/{client_id}")
                        if response.status_code == 200:
                            mascotas_cliente = response.json()
                            if mascotas_cliente:
                                mascota_nombres = ["Seleccione una mascota"] + [
                                    f"{m['nombre_mascota']} ({m['raza']})" 
                                    for m in mascotas_cliente
                                ]
                                mascota_seleccionada = st.selectbox(
                                    "Mascota",
                                    options=mascota_nombres,
                                    key="mascota_select"
                                )
                                if mascota_seleccionada != "Seleccione una mascota":
                                    mascota_id = next(
                                        m['id_mascota'] for m in mascotas_cliente 
                                        if f"{m['nombre_mascota']} ({m['raza']})" == mascota_seleccionada
                                    )
                            else:
                                st.warning("Este cliente no tiene mascotas registradas")
                                mascota_seleccionada = st.selectbox(
                                    "Mascota",
                                    options=["No hay mascotas disponibles"],
                                    key="mascota_select_none"
                                )
                                mascota_id = None
                    else:
                        mascota_seleccionada = st.selectbox(
                            "Mascota",
                            options=["Seleccione un cliente primero"],
                            disabled=True,
                            key="mascota_select_disabled"
                        )
                        mascota_id = None
                else:
                    st.error("Error al cargar los clientes")
                    client_id = None
                    mascota_id = None
            except Exception as e:
                st.error(f"Error al cargar datos: {str(e)}")
                client_id = None
                mascota_id = None
        
                    # Método de Pago
            metodo_pago = st.selectbox(
                "Método de Pago (Opcional)",
                options=["Sin Especificar", "Efectivo", "Tarjeta", "Bizum", "Transferencia"]
            )


        with col2:
            st.subheader("💉 Detalles del Tratamiento")
            
            # Tratamiento
            try:
                response = requests.get("http://localhost:8000/tratamientos/")
                if response.status_code == 200:
                    tratamientos = response.json()
                    tratamiento_nombres = ["Seleccione un tratamiento"] + [
                        t['nombre_tratamiento'] for t in tratamientos
                    ]
                    tratamiento_seleccionado = st.selectbox(
                        "Tratamiento",
                        options=tratamiento_nombres
                    )
                    
                    if tratamiento_seleccionado != "Seleccione un tratamiento":
                        tratamiento = next(t for t in tratamientos 
                                        if t['nombre_tratamiento'] == tratamiento_seleccionado)
                        descripcion = tratamiento['descripcion']
                        tratamiento_id = tratamiento['id_tratamiento']
                    else:
                        descripcion = ""
                        tratamiento_id = None
                    
                    st.text_area(
                        "Descripción",
                        value=descripcion,
                        disabled=True,
                        height=206
                    )
                else:
                    st.error("Error al cargar tratamientos")
                    tratamiento_id = None
            except Exception as e:
                st.error(f"Error al cargar tratamientos: {str(e)}")
                tratamiento_id = None

            # Estado
            estado = st.selectbox(
                "Estado",
                options=["Pendiente", "Confirmada", "En Proceso", "Finalizada", "Cancelada"]
            )


        # Botón centrado
        col1, col2, col3 = st.columns([4.7,2,4])
        with col2:
            submitted = st.form_submit_button("Guardar Cita")

        if submitted:
            if not all([client_id, mascota_id, tratamiento_id]):
                st.error("Por favor, complete todos los campos obligatorios")
                return

            try:
                cita_data = {
                    "fecha": datetime.combine(fecha, hora).isoformat(),
                    "descripcion": descripcion,
                    "estado": estado,
                    "id_mascota": mascota_id,
                    "id_cliente": client_id,
                    "id_tratamiento": tratamiento_id,
                    "metodo_pago": None if metodo_pago == "Sin Especificar" else metodo_pago
                }

                response = requests.post("http://localhost:8000/citas/", json=cita_data)
                if response.status_code == 201:
                    st.success("¡Cita registrada exitosamente!")
                else:
                    st.error(f"Error al registrar la cita: {response.text}")
            except Exception as e:
                st.error(f"Error al procesar la cita: {str(e)}")

def show_citas_list():
    """
    Muestra la lista de citas con opciones de filtrado y gestión
    """
    st.subheader("📋 Lista de Citas")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        estado_filtro = st.multiselect("Estado",
            ["Pendiente", "Confirmada", "Finalizada", "Cancelada"])
    with col2:
        fecha_filtro = st.date_input("Fecha")

    try:
        response = requests.get("http://localhost:8000/citas/")
        if response.status_code == 200:
            citas = response.json()
            df = pd.DataFrame(citas)
            
            # Aplicar filtros
            if estado_filtro:
                df = df[df['estado'].isin(estado_filtro)]
            if fecha_filtro:
                df['fecha'] = pd.to_datetime(df['fecha'])
                df = df[df['fecha'].dt.date == fecha_filtro]
            
            # Mostrar citas
            for _, cita in df.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([3,2,1])
                    
                    with col1:
                        st.markdown(f"### 📅 {cita['fecha']}")
                        st.write(f"📝 **Descripción:** {cita['descripcion']}")
                        
                    with col2:
                        st.write(f"👤 **Cliente ID:** {cita['id_cliente']}")
                        st.write(f"🐾 **Mascota ID:** {cita['id_mascota']}")
                        st.write(f"💉 **Tratamiento ID:** {cita['id_tratamiento']}")
                        
                    with col3:
                        estado_color = {
                            "Pendiente": "🟡",
                            "Confirmada": "🟢",
                            "Finalizada": "🔵",
                            "Cancelada": "🔴"
                        }
                        st.write(f"Estado: {estado_color.get(cita['estado'], '⚪')} {cita['estado']}")
                        
                        if cita['estado'] in ['Pendiente', 'Confirmada']:
                            if st.button("✏️ Editar", key=f"edit_{cita['id_cita']}"):
                                show_edit_form(cita)
                            if st.button("❌ Cancelar", key=f"cancel_{cita['id_cita']}"):
                                cancel_cita(cita['id_cita'])
                    st.markdown("---")
        else:
            st.error("Error al cargar las citas")
    except Exception as e:
        st.error(f"Error: {str(e)}")

@st.dialog("Editar Cita")
def show_edit_form(cita):
    """
    Muestra un formulario para editar una cita
    """
    with st.form("form_editar_cita"):
        fecha = st.date_input("Fecha de la cita", value=pd.to_datetime(cita['fecha']).date())
        descripcion = st.text_area("Descripción", value=cita['descripcion'])
        estado = st.selectbox("Estado", ["Pendiente", "Confirmada", "Finalizada", "Cancelada"], index=["Pendiente", "Confirmada", "Finalizada", "Cancelada"].index(cita['estado']))
        
        submitted = st.form_submit_button("Guardar Cambios")
        if submitted:
            updated_cita = {
                "fecha": fecha.isoformat(),
                "descripcion": descripcion,
                "estado": estado
            }
            response = requests.put(f"http://localhost:8000/citas/{cita['id_cita']}", json=updated_cita)
            if response.status_code == 200:
                st.success("Cita actualizada exitosamente")
                st.experimental_rerun()
            else:
                st.error("Error al actualizar la cita")

def cancel_cita(id_cita):
    """
    Cancela una cita existente
    """
    response = requests.delete(f"http://localhost:8000/citas/{id_cita}")
    if response.status_code == 200:
        st.success("Cita cancelada exitosamente")
        st.experimental_rerun()
    else:
        st.error("Error al cancelar la cita")

def show_buscar_citas():
    """
    Muestra la interfaz de búsqueda de citas con opciones de filtro
    """
    st.subheader("🔍 Buscar Citas")

    # Campos de filtro
    col1, col2, col3 = st.columns(3)
    with col1:
        dni_cliente = st.text_input("DNI del Cliente")
    with col2:
        nombre_cliente = st.text_input("Nombre del Cliente")
    with col3:
        nombre_tratamiento = st.text_input("Nombre del Tratamiento")

    # Fecha de la Cita - Campo vacío por defecto
    fecha_cita_str = st.text_input("Fecha de la Cita (Opcional, formato: YYYY-MM-DD)")

    # Inicializar la variable fecha_cita
    fecha_cita = None

    # Verificar si se ingresó una fecha y si es válida
    if fecha_cita_str:
        try:
            fecha_cita = datetime.strptime(fecha_cita_str, "%Y-%m-%d")
        except ValueError:
            st.error("El formato de la fecha debe ser YYYY-MM-DD")

    busqueda = st.text_input("Buscar por descripción o ID")

    # Botón de búsqueda
    if st.button("Buscar"):
        try:
            # Creación del diccionario de parámetros para la búsqueda
            params = {
                "dni_cliente": dni_cliente,
                "nombre_cliente": nombre_cliente,
                "nombre_tratamiento": nombre_tratamiento,
                "q": busqueda
            }

            # Solo agregar "fecha_cita" si se ingresó una fecha válida
            if fecha_cita:
                params["fecha_cita"] = fecha_cita.strftime("%Y-%m-%d")

            response = requests.get(f"http://localhost:8000/citas/", params=params)
            if response.status_code == 200:
                citas = response.json()
                if citas:
                    for cita in citas:
                        st.write(f"📅 Fecha: {cita['fecha']}")
                        st.write(f"🧑‍⚕️ Cliente: {cita['cliente']}")
                        st.write(f"🐾 Mascota: {cita['mascota']}")
                        st.write(f"💉 Tratamiento: {cita['tratamiento']}")
                        st.write(f"Estado: {cita['estado']}")
                        st.markdown("---")
                else:
                    st.info("No se encontraron citas que coincidan con los filtros")
        except Exception as e:
            st.error(f"Error al buscar citas: {str(e)}")


if __name__ == "__main__":
    show()