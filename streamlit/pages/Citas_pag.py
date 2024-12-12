import streamlit as st
import logging
import pandas as pd
from streamlit_calendar import calendar
from datetime import datetime, timedelta
import requests
import json
import tempfile
import os


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

            # Cliente - Celda independiente
            try:
                response = requests.get("http://localhost:8000/clientes/")
                if response.status_code == 200:
                    clientes = response.json()
                    cliente_nombres = ["Seleccione un cliente"] + [
                        f"{c['nombre_cliente']} (DNI: {c['dni']})" for c in clientes
                    ]
                    cliente_seleccionado = st.selectbox(
                        "Seleccione un cliente",
                        options=cliente_nombres,
                        key="cliente_select"
                    )
                else:
                    st.error("Error al cargar los clientes.")
            except Exception as e:
                st.error(f"Error al cargar los clientes: {str(e)}")

            # Mascota - Celda independiente
            try:
                mascota_response = requests.get("http://localhost:8000/mascotas/")
                if mascota_response.status_code == 200:
                    mascotas = mascota_response.json()

                    # Combinar datos de mascotas y clientes
                    mascota_opciones = ["Seleccione una mascota"]
                    for mascota in mascotas:
                        # Buscar cliente asociado a la mascota
                        cliente = next(
                            (c for c in clientes if c['id_cliente'] == mascota['id_cliente']),
                            None
                        )
                        if cliente:
                            cliente_nombre = f"{cliente['nombre_cliente']} (DNI: {cliente['dni']})"
                            mascota_opciones.append(f"{mascota['nombre_mascota']} ({mascota['raza']}) - Cliente: {cliente_nombre}")
                        else:
                            mascota_opciones.append(f"{mascota['nombre_mascota']} ({mascota['raza']}) - Cliente: Desconocido")

                    mascota_seleccionada = st.selectbox(
                        "Seleccione una mascota",
                        options=mascota_opciones,
                        key="mascota_select"
                    )
                else:
                    st.error("Error al cargar las mascotas.")
            except Exception as e:
                st.error(f"Error al cargar las mascotas: {str(e)}")

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
                        tratamiento_id = tratamiento['id_tratamiento']
                    else:
                        tratamiento_id = None
                else:
                    st.error("Error al cargar tratamientos.")
            except Exception as e:
                st.error(f"Error al cargar tratamientos: {str(e)}")

            # Campo de texto para una descripción personalizada de la cita
            descripcion = st.text_area(
                "Descripción de la Cita",
                placeholder="Ingrese aquí los detalles de la cita...",
                height=150
            )

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
            if cliente_seleccionado == "Seleccione un cliente" or mascota_seleccionada == "Seleccione una mascota" or tratamiento_seleccionado == "Seleccione un tratamiento":
                st.error("Por favor, complete todos los campos obligatorios.")
                return

            try:
                # Preparar datos de la cita
                cita_data = {
                    "fecha": datetime.combine(fecha, hora).isoformat(),
                    "descripcion": descripcion,
                    "estado": estado,
                    "id_mascota": next(m['id_mascota'] for m in mascotas if f"{m['nombre_mascota']} ({m['raza']})" in mascota_seleccionada),
                    "id_cliente": next(c['id_cliente'] for c in clientes if f"{c['nombre_cliente']} (DNI: {c['dni']})" == cliente_seleccionado),
                    "id_tratamiento": tratamiento_id,
                    "metodo_pago": None if metodo_pago == "Sin Especificar" else metodo_pago
                }

                # Enviar datos al backend
                response = requests.post("http://localhost:8000/citas/", json=cita_data)
                if response.status_code == 201:
                    st.success("¡Cita registrada exitosamente!")
                else:
                    st.error(f"Error al registrar la cita: {response.text}")
            except Exception as e:
                st.error(f"Error al procesar la cita: {str(e)}")




def show_finalize_form(cita):
    """Muestra el formulario para finalizar una cita y generar factura"""
    with st.container():
        st.markdown("""
            <style>
            .finalize-form {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin: 20px 0;
            }
            .stSelectbox > div {
                min-height: 45px;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="finalize-form">', unsafe_allow_html=True)
        st.subheader("🏁 Finalizar Cita")
        
        metodo_pago = st.selectbox(
            "💰 Método de pago",
            ["Efectivo", "Tarjeta", "Bizum", "Transferencia"],
            key=f"pago_{cita['id_cita']}"
        )

        cols = st.columns(2)
        
        with cols[0]:
            if st.button("✅ Confirmar y Generar Factura", key=f"confirm_{cita['id_cita']}"):
                try:
                    # Finalizar la cita
                    response = requests.put(
                        f"http://localhost:8000/citas/finalizar/{cita['id_cita']}",
                        params={"metodo_pago": metodo_pago}
                    )
                    
                    if response.status_code == 200:
                        # Generar y descargar factura
                        factura_response = requests.get(
                            f"http://localhost:8000/tratamientos/factura/generar/{cita['id_tratamiento']}"
                        )
                        if factura_response.status_code == 200:
                            st.success("✅ Cita finalizada exitosamente")

                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                                tmp_file.write(factura_response.content)
                                tmp_file.flush()

                            # Descargar el archivo temporal
                            with open(tmp_file.name, "rb") as file:
                                st.download_button(
                                    label="📥 Descargar Factura",
                                    data=file,
                                    file_name=f"factura_cita_{cita['id_cita']}.pdf",
                                    mime="application/pdf"
                                )

                            # Eliminar el archivo temporal
                            os.unlink(tmp_file.name)
                        else:
                            st.error("❌ Error al generar la factura")

                        st.rerun()
                    else:
                        st.error("❌ Error al finalizar la cita")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

                

        with cols[1]:
            if st.button("❌ Cancelar", key=f"cancel_{cita['id_cita']}"):
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

def show_citas_list():
    """
    Muestra la interfaz de búsqueda y lista de citas
    """
    st.title("📋 Lista de Citas")

    # Filtros en dos filas
    col1, col2 = st.columns(2)
    with col1:
        nombre_filtro = st.text_input(
            label="Filtrar por Cliente",
            key="nombre_filtro",
            placeholder="Nombre del Cliente",
            label_visibility="hidden"
        )
    with col2:
        dni_filtro = st.text_input(
            label="Filtrar por DNI",
            key="dni_filtro",
            placeholder="DNI del Cliente",
            label_visibility="hidden"
        )

    col3, col4 = st.columns(2)
    with col3:
        fecha_filtro = st.text_input(
            label="Filtrar por Fecha (YYYY-MM-DD)",
            key="fecha_filtro",
            placeholder="Fecha (YYYY-MM-DD)",
            label_visibility="hidden"
        )
    with col4:
        estado_filtro = st.selectbox(
            "Estado",
            ["Todos", "Pendiente", "Confirmada", "En Proceso", "Finalizada", "Cancelada"],
            key="estado_filtro"
        )

    try:
        # Obtener todas las citas
        response = requests.get("http://localhost:8000/citas/")
        if response.status_code == 200:
            citas = response.json()
            if citas:
                citas_filtradas = []
                for cita in citas:
                    # Obtener datos relacionados usando los endpoints específicos
                    cliente_response = requests.get(f"http://localhost:8000/clientes/{cita['id_cliente']}")
                    mascota_response = requests.get(f"http://localhost:8000/mascotas/{cita['id_mascota']}")
                    tratamiento_response = requests.get(f"http://localhost:8000/tratamientos/{cita['id_tratamiento']}")

                    if cliente_response.status_code == 200 and mascota_response.status_code == 200 and tratamiento_response.status_code == 200:
                        cliente = cliente_response.json()
                        mascota = mascota_response.json()
                        tratamiento = tratamiento_response.json()
                    else:
                        st.error("Error al cargar los datos relacionados para una cita.")
                        continue

                    # Aplicar filtros
                    if nombre_filtro and nombre_filtro.lower() not in cliente['nombre_cliente'].lower():
                        continue
                    if dni_filtro and dni_filtro.lower() not in cliente['dni'].lower():
                        continue
                    if fecha_filtro and fecha_filtro not in cita['fecha']:
                        continue
                    if estado_filtro != "Todos" and estado_filtro != cita['estado']:
                        continue
                    
                    citas_filtradas.append({**cita, 'cliente': cliente, 'mascota': mascota, 'tratamiento': tratamiento})

                if not citas_filtradas:
                    st.info("No se encontraron citas con los filtros especificados")
                    return

                for cita in citas_filtradas:
                    with st.container():
                        st.markdown("""
                            <div style="border:1px solid #ddd; border-radius:10px; padding:15px; 
                            margin-bottom:20px; background-color:#f8f9fa;">
                        """, unsafe_allow_html=True)
                        
                        cols = st.columns([3, 2, 2])
                        
                        with cols[0]:
                            st.markdown(f"### 📅 {cita['fecha']}")
                            st.write(f"👤 **Cliente:** {cita['cliente']['nombre_cliente']}")
                            st.write(f"🐾 **Mascota:** {cita['mascota']['nombre_mascota']}")

                        with cols[1]:
                            st.write(f"🏥 **Tratamiento:** {cita['tratamiento']['nombre_tratamiento']}")
                            st.write(f"📝 **Descripción:** {cita['descripcion']}")
                            if cita['metodo_pago']:
                                st.write(f"💰 **Método de Pago:** {cita['metodo_pago']}")

                        with cols[2]:
                            # Botones de acción
                            st.markdown("""
                                <style>
                                .action-button {
                                    width: 100%;
                                    margin: 5px 0;
                                    padding: 10px;
                                    border-radius: 5px;
                                    text-align: center;
                                }
                                </style>
                            """, unsafe_allow_html=True)

                            # Estado de la cita
                            estado_color = {
                                "Pendiente": "🟡",
                                "Confirmada": "🟢",
                                "Finalizada": "🔵",
                                "Cancelada": "🔴"
                            }
                            st.write(f"Estado: {estado_color.get(cita['estado'], '⚪')} {cita['estado']}")

                            # Botones
                            if st.button("✏️ Editar", key=f"edit_{cita['id_cita']}", use_container_width=True):
                                show_edit_form(cita)

                            if cita['estado'] not in ['Finalizada', 'Cancelada']:
                                if st.button("❌ Cancelar", key=f"delete_{cita['id_cita']}", use_container_width=True):
                                    cancel_cita(cita['id_cita'])
                                
                                if st.button("✅ Finalizar", key=f"finish_{cita['id_cita']}", use_container_width=True):
                                    show_finalize_form(cita)
                        st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.error("Error al cargar la lista de citas")
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
                st.rerun()
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
        st.rerun()
    else:
        st.error("Error al cancelar la cita")


if __name__ == "__main__":
    show()