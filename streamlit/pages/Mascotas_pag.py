import streamlit as st
import requests
import plotly.express as px
import pandas as pd
from datetime import datetime

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

    st.title("Gestión de Mascotas 🐾")
    
    tabs = st.tabs(["📝Nueva Mascota","📋Lista de Mascotas"])
    
    with tabs[0]:
        show_nueva_mascota()
    
    with tabs[1]:
        show_mascotas_list()

def show_mascotas_list():
    st.title("📋 Lista de Mascotas")

    col1, col2 = st.columns(2)
    with col1:
        nombre_filtro = st.text_input(
            label="Filtrar por Nombre",
            placeholder="Nombre de la Mascota",
            label_visibility="hidden"
        )
    with col2:
        raza_filtro = st.text_input(
            label="Filtrar por Raza",
            placeholder="Raza",
            label_visibility="hidden"
        )

    col3, col4 = st.columns(2)
    with col3:
        cliente_filtro = st.text_input(
            label="Filtrar por Cliente",
            placeholder="Nombre del Cliente",
            label_visibility="hidden"
        )
    with col4:
        estado_filtro = st.selectbox(
            "Estado",
            ["Todos", "Vivo", "Fallecido"]
        )

    try:
        response = requests.get("http://fastapi:8000/mascotas/")
        if response.status_code == 200:
            mascotas = response.json()
            if mascotas:
                mascotas_filtradas = []
                for mascota in mascotas:
                    cliente_response = requests.get(f"http://fastapi:8000/clientes/{mascota['id_cliente']}")
                    if cliente_response.status_code == 200:
                        cliente = cliente_response.json()
                        
                        if nombre_filtro and nombre_filtro.lower() not in mascota['nombre_mascota'].lower():
                            continue
                        if raza_filtro and raza_filtro.lower() not in mascota['raza'].lower():
                            continue
                        if cliente_filtro and cliente_filtro.lower() not in cliente['nombre_cliente'].lower():
                            continue
                        if estado_filtro != "Todos" and estado_filtro != mascota['estado']:
                            continue
                        
                        mascotas_filtradas.append({**mascota, 'cliente': cliente})

                if not mascotas_filtradas:
                    st.info("No se encontraron mascotas con los filtros especificados")
                else:
                    for mascota in mascotas_filtradas:
                        with st.container():
                            st.markdown("""
                                <div style="border:1px solid #ddd; border-radius:10px; padding:15px; 
                                margin-bottom:20px; background-color:#f8f9fa;">
                            """, unsafe_allow_html=True)
                            
                            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                            
                            with col1:
                                st.markdown(f"### 🐾 {mascota['nombre_mascota']}")
                                st.write(f"👤 **Cliente:** {mascota['cliente']['nombre_cliente']}")
                                st.write(f"📅 **Edad:** {mascota['edad']} años")
                            
                            with col2:
                                st.write(f"🦮 **Raza:** {mascota['raza']}")
                                if mascota['afeccion']:
                                    st.write(f"🏥 **Afección:** {mascota['afeccion']}")
                            
                            with col3:
                                estado_color = {
                                    "Vivo": "🟢",
                                    "Fallecido": "⚫"
                                }
                                st.write(f"Estado: {estado_color.get(mascota['estado'], '⚪')} {mascota['estado']}")

                            with col4:
                                col_edit, col_delete = st.columns(2)
                                with col_edit:
                                    if st.button("✏️", key=f"edit_{mascota['id_mascota']}"):
                                        show_edit_form(mascota)
                                with col_delete:
                                    if st.button("❌", key=f"delete_{mascota['id_mascota']}"):
                                        delete_mascota(mascota['id_mascota'])
                            
                            st.markdown("</div>", unsafe_allow_html=True)
                    
                    if st.button("📥 Exportar Mascotas"):
                        response = requests.post("http://fastapi:8000/mascotas/exportar")
                        if response.status_code == 200:
                            st.success("Mascotas exportadas exitosamente")
                        else:
                            st.error("Error al exportar mascotas")
            else:
                st.info("No hay mascotas registradas")
        else:
            st.error("Error al cargar las mascotas")
    except Exception as e:
        st.error(f"Error: {str(e)}")


def show_nueva_mascota():
    st.subheader("📝 Registrar Nueva Mascota")
    
    with st.form("form_nueva_mascota", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("🐾 Nombre de la Mascota")
            raza = st.text_input("🦮 Raza")
            edad = st.number_input("📅 Edad", min_value=0, max_value=50)

        with col2:
            afeccion = st.text_input("🏥 Afección (opcional)")
            estado = st.selectbox("Estado", ["Vivo", "Fallecido"])
            
            try:
                response = requests.get("http://fastapi:8000/clientes/")
                if response.status_code == 200:
                    clientes = response.json()
                    cliente_opciones = ["Seleccione un cliente"] + [
                        f"{c['nombre_cliente']} (DNI: {c['dni']})" 
                        for c in clientes
                    ]
                    cliente_seleccionado = st.selectbox("Cliente", options=cliente_opciones)
            except Exception as e:
                st.error(f"Error al cargar clientes: {str(e)}")
                cliente_seleccionado = None
        
        submitted = st.form_submit_button("Registrar Mascota")
        
        if submitted:
            if not all([nombre, raza, edad, cliente_seleccionado != "Seleccione un cliente"]):
                st.error("Por favor complete todos los campos obligatorios")
                return

            try:
                dni_seleccionado = cliente_seleccionado.split("DNI: ")[1].strip(")")
                id_cliente = next(c['id_cliente'] for c in clientes if c['dni'] == dni_seleccionado)
                
                mascota_data = {
                    "nombre_mascota": nombre,
                    "raza": raza,
                    "edad": edad,
                    "afeccion": afeccion,
                    "estado": estado,
                    "id_cliente": id_cliente
                }

                response = requests.post("http://fastapi:8000/mascotas/", json=mascota_data)
                if response.status_code == 201:
                    st.success("¡Mascota registrada exitosamente!")
                else:
                    st.error(f"Error al registrar la mascota: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

@st.dialog("Editar Mascota")
def show_edit_form(mascota):
    with st.form("form_editar_mascota"):
        nombre = st.text_input("Nombre", value=mascota['nombre_mascota'])
        raza = st.text_input("Raza", value=mascota['raza'])
        edad = st.number_input("Edad", value=mascota['edad'], min_value=0, max_value=50)
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
                st.error(f"Error: {str(e)}")

def delete_mascota(id_mascota):
    try:
        response = requests.delete(f"http://fastapi:8000/mascotas/{id_mascota}")
        if response.status_code == 200:
            st.success("Mascota eliminada exitosamente")
            st.rerun()
        else:
            st.error("Error al eliminar la mascota")
    except Exception as e:
        st.error(f"Error: {str(e)}")