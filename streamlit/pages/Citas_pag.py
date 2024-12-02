import streamlit as st
import logging
import pandas as pd
from streamlit_calendar import calendar
from datetime import datetime, timedelta
import requests
import json


# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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

    # Título principal con estilo
    st.markdown("""
        <h1 style='color: #1f2937; font-size: 2.5rem; margin-bottom: 2rem;'>
            Gestión de Citas Veterinarias 📆
        </h1>
    """, unsafe_allow_html=True)

    # Crear las pestañas para la navegación con mejor estilo
    tabs = st.tabs([
        "🗓️ Calendario de Citas",
        "📝 Nueva Cita",
        "📋 Lista de Citas"
    ])

    with tabs[0]:
        st.markdown("""
            <h2 style='color: #2563eb; font-size: 1.5rem; margin-bottom: 1.5rem;'>
                Calendario de Citas
            </h2>
        """, unsafe_allow_html=True)
        show_calendar()

    with tabs[1]:
        show_nueva_cita()

    with tabs[2]:
        show_citas_list()
        

def show_calendar():
    """Muestra el calendario interactivo con las citas programadas"""

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


    calendar_options = {
        "editable": True,
        "navLinks": True,
        "selectable": True,
        "slotMinTime": "08:00:00",  # Hora inicial del calendario
        "slotMaxTime": "20:00:00",  # Hora final del calendario
        "initialView": "timeGridWeek",  # Vista inicial (semana)
        "resourceGroupField": "building",
        "headerToolbar": {
            "left": "prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek"  # Opciones de vista
        },
        "slotDuration": "00:30:00",  # Duración de cada intervalo (30 minutos)
        "slotLabelInterval": "00:30:00",  # Intervalo entre etiquetas (opcional)
        "allDaySlot": False,  # Ocultar la fila de "todo el día"
        "slotLabelFormat": {  # Formato de las etiquetas de tiempo
            "hour": "2-digit",
            "minute": "2-digit",
            "hour12": True
        },
        "height": 1300,  # Altura del calendario
        "aspectRatio": 1.5  # Relación de aspecto
    }



    # CSS mejorado para el calendario
    custom_calendar_css = """
        /* Contenedor principal del calendario */
        .fc {
            background: white;
            font-family: system-ui, -apple-system, sans-serif;
        }

        /* Cabecera y controles */
        .fc-toolbar {
            padding: 1rem;
            background: #f8fafc;
            border-radius: 8px;
            margin-bottom: 1rem !important;
        }

        .fc-toolbar-title {
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            color: #1e293b !important;
        }

        /* Botones de navegación */
        .fc-button {
            background: #3b82f6 !important;
            border: none !important;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2) !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
            transition: all 0.2s !important;
        }

        .fc-button:hover {
            background: #2563eb !important;
            transform: translateY(-1px);
        }

        .fc-button-active {
            background: #1d4ed8 !important;
        }

        /* Celdas de tiempo */
        .fc-timegrid-slot {
            height: 3rem !important;
            border-color: #e5e7eb !important;
        }

        .fc-timegrid-slot-label {
            font-size: 0.875rem !important;
            color: #6b7280 !important;
        }

        /* Eventos */
        .fc-event {
            border: none !important;
            border-radius: 6px !important;
            padding: 4px 8px !important;
            margin: 1px !important;
            transition: transform 0.2s !important;
        }

        .fc-event:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .fc-event-title {
            font-weight: 600 !important;
            font-size: 0.875rem !important;
            padding: 2px 0 !important;
        }

        .fc-event-time {
            font-size: 0.75rem !important;
            opacity: 0.9;
        }

        /* Columnas de recursos */
        .fc-resource-group-cell {
            background: #f1f5f9 !important;
            font-weight: 600 !important;
            color: #334155 !important;
            text-transform: uppercase;
            font-size: 0.75rem !important;
            letter-spacing: 0.05em;
        }

        /* Linea de tiempo actual */
        .fc-timegrid-now-indicator-line {
            border-color: #ef4444 !important;
        }

        .fc-timegrid-now-indicator-arrow {
            border-color: #ef4444 !important;
            background: #ef4444 !important;
        }

        /* Hover en slots de tiempo */
        .fc-timegrid-col-bg .fc-highlight {
            background: rgba(59, 130, 246, 0.1) !important;
        }
    """

    # Renderizar el calendario
    events = cargar_citas()
    state = calendar(
        events=st.session_state.get("events", events),
        options=calendar_options,
        custom_css=custom_calendar_css,
        key='calendar'
    )

    # Manejo de eventos
    if state.get("eventsSet") is not None:
        st.session_state["events"] = state["eventsSet"]

    if state.get('select') is not None:
        st.session_state["time_inicial"] = datetime.fromisoformat(state["select"]["start"])
        st.session_state["time_final"] = datetime.fromisoformat(state["select"]["end"])
        st.switch_page("Nueva Cita")

    st.markdown('</div>', unsafe_allow_html=True)

def show_nueva_cita():
    """
    Formulario de nueva cita
    """
    st.markdown("""
    <style>
        /* Contenedor general del formulario */
        div.form-group {
            background-color: white !important;
            padding: 2rem !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
            margin: 1rem auto !important;
            width: 80% !important;
        }

        /* Títulos */
        div.form-group h1, 
        div.form-group h2, 
        div.form-group h3 {
            color: #1E293B !important;
            font-family: 'Arial', sans-serif !important;
            font-weight: bold !important;
            margin-bottom: 1rem !important;
        }

        /* Inputs */
        div.form-group .stDateInput > div, 
        div.form-group .stTimeInput > div, 
        div.form-group .stSelectbox > div {
            margin-bottom: 1rem !important;
            font-size: 1rem !important;
        }

        /* Botón Guardar */
        div.form-group .stButton > button {
            background: linear-gradient(180deg, #3b82f6 0%, #2563eb 100%) !important;
            color: white !important;
            font-weight: bold !important;
            font-size: 1rem !important;
            padding: 0.5rem 1rem !important;
            border: none !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2) !important;
            transition: all 0.2s ease !important;
        }

        div.form-group .stButton > button:hover {
            background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%) !important;
            box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3) !important;
            transform: translateY(-1px) !important;
        }

        /* Columnas */
        div.stColumn {
            padding: 1rem !important;
        }

        /* Inputs generales */
        .stDateInput > div, 
        .stTimeInput > div, 
        .stSelectbox > div {
            margin-bottom: 1rem !important;
            font-size: 1rem !important;
        }

        /* Botón general de Streamlit */
        .stButton > button {
            background: linear-gradient(180deg, #3b82f6 0%, #2563eb 100%) !important;
            color: white !important;
            font-weight: bold !important;
            font-size: 1rem !important;
            padding: 0.5rem 1rem !important;
            border: none !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2) !important;
            transition: all 0.2s ease !important;
        }

        .stButton > button:hover {
            background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%) !important;
            box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3) !important;
            transform: translateY(-1px) !important;
        }

        /* Centrado de botones */
        .stButton {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }
    </style>
    """, unsafe_allow_html=True)


    # Abre el contenedor estilizado
    st.markdown('<div class="form-group">', unsafe_allow_html=True)

    st.title("Nueva Cita 📝")

    with st.form("form_nueva_cita", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📅 Detalles de la Cita")
            
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
            st.markdown("### 💉 Detalles del Tratamiento")
            
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
        col1, col2, col3 = st.columns([4.7, 2, 4])
        with col2:
             submitted = st.form_submit_button("💾 Guardar Cita")
        
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

    # Cierra el contenedor del formulario
    st.markdown('</div>', unsafe_allow_html=True)


def show_citas_list():
    """
    Muestra la interfaz de búsqueda y lista de citas
    """
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Buscar Citas")

    # Almacenar valores de búsqueda en st.session_state para mantener el estado
    col1, col2, col3 = st.columns(3)
    with col1:
        if 'dni_cliente' not in st.session_state:
            st.session_state.dni_cliente = ''
        st.session_state.dni_cliente = st.text_input("DNI del Cliente", value=st.session_state.dni_cliente)
        
    with col2:
        if 'nombre_cliente' not in st.session_state:
            st.session_state.nombre_cliente = ''
        st.session_state.nombre_cliente = st.text_input("Nombre del Cliente", value=st.session_state.nombre_cliente)

    with col3:
        if 'nombre_tratamiento' not in st.session_state:
            st.session_state.nombre_tratamiento = ''
        st.session_state.nombre_tratamiento = st.text_input("Nombre del Tratamiento", value=st.session_state.nombre_tratamiento)

    # Fecha de la Cita
    if 'fecha_cita_str' not in st.session_state:
        st.session_state.fecha_cita_str = ''
    st.session_state.fecha_cita_str = st.text_input("Fecha de la Cita (Opcional, formato: YYYY-MM-DD)", value=st.session_state.fecha_cita_str)

    # Botón de búsqueda
    buscar_clicked = st.button("Buscar")

    st.markdown("---")  # Separador
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 📋 Lista de Citas")

    # Filtros para la lista
    col1, col2 = st.columns(2)
    with col1:
        estado_filtro = st.multiselect("Estado", ["Pendiente", "Confirmada", "Finalizada", "Cancelada"])
    with col2:
        fecha_filtro = st.date_input("Fecha")

    # Mantener el estado de búsqueda al presionar el botón
    if buscar_clicked:
        st.session_state.buscar = True

    try:
        if st.session_state.get('buscar', False):
            # Parámetros de búsqueda
            params = {
                "dni_cliente": st.session_state.dni_cliente,
                "nombre_cliente": st.session_state.nombre_cliente,
                "nombre_tratamiento": st.session_state.nombre_tratamiento,
                "q": st.session_state.fecha_cita_str
            }

            if st.session_state.fecha_cita_str:
                try:
                    fecha_cita = datetime.strptime(st.session_state.fecha_cita_str, "%Y-%m-%d")
                    params["fecha_cita"] = fecha_cita.strftime("%Y-%m-%d")
                except ValueError:
                    st.error("El formato de la fecha debe ser YYYY-MM-DD")

            # Solicitud al servidor con los filtros
            response = requests.get(f"http://localhost:8000/citas/", params=params)
            if response.status_code == 200:
                citas = response.json()
                if citas:
                    for cita in citas:
                        with st.container():
                            col1, col2, col3 = st.columns([3, 2, 1])

                            with col1:
                                st.markdown(f"### 📅 {cita['fecha']}")
                                st.write(f"📝 **Descripción:** {cita.get('descripcion', 'No disponible')}")

                            with col2:
                                # Obtener datos del cliente
                                cliente_response = requests.get(f"http://localhost:8000/clientes/{cita['id_cliente']}")
                                if cliente_response.status_code == 200:
                                    cliente = cliente_response.json()
                                    st.write(f"👤 **Cliente:** {cliente.get('nombre_cliente', 'No disponible')}")
                                else:
                                    st.write("👤 **Cliente:** Error al cargar datos")

                                # Obtener datos de la mascota
                                mascota_response = requests.get(f"http://localhost:8000/mascotas/{cita['id_mascota']}")
                                if mascota_response.status_code == 200:
                                    mascota = mascota_response.json()
                                    st.write(f"🐾 **Mascota:** {mascota.get('nombre_mascota', 'No disponible')}")
                                else:
                                    st.write("🐾 **Mascota:** Error al cargar datos")

                                # Obtener datos del tratamiento
                                tratamiento_response = requests.get(f"http://localhost:8000/tratamientos/{cita['id_tratamiento']}")
                                if tratamiento_response.status_code == 200:
                                    tratamiento = tratamiento_response.json()
                                    st.write(f"💉 **Tratamiento:** {tratamiento.get('nombre_tratamiento', 'No disponible')}")
                                else:
                                    st.write("💉 **Tratamiento:** Error al cargar datos")

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
                    st.info("No se encontraron citas que coincidan con los filtros")

    
        # Mostrar lista completa con filtros
        if not st.session_state.get('buscar', False):
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
                        col1, col2, col3 = st.columns([3, 2, 1])

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

def obtener_datos_cliente(id_cliente):
    """
    Obtiene los datos de un cliente específico de la lista de clientes
    """
    try:
        response = requests.get("http://localhost:8000/clientes/")
        if response.status_code == 200:
            clientes = response.json()
            cliente = next((c for c in clientes if c['id_cliente'] == id_cliente), None)
            return cliente
    except Exception as e:
        logger.error(f"Error al obtener datos del cliente: {str(e)}")
        return None
    return None



@st.dialog("Editar Cita")
def show_edit_form(cita):
    """
    Muestra un formulario para editar una cita
    """
    st.markdown('<div class="form-group">', unsafe_allow_html=True)
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

    st.markdown('</div>', unsafe_allow_html=True)

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


if __name__ == "__main__":
    show()