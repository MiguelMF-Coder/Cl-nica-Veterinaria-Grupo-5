import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime, timedelta

def show():
    st.title("Dashboard Analítico 📊")
    
    # Navegación
    tabs = st.tabs([
        "📈 Resumen General",
        "👥 Análisis de Clientes",
        "🐾 Análisis de Mascotas",
        "🏥 Análisis de Tratamientos",
        "📅 Análisis de Citas"
    ])

    with tabs[0]:
        show_resumen_general()
    with tabs[1]:
        show_analisis_clientes()
    with tabs[2]:
        show_analisis_mascotas()
    with tabs[3]:
        show_analisis_tratamientos()
    with tabs[4]:
        show_analisis_citas()

def show_resumen_general():
    st.header("Resumen General")
    
    try:
        col1, col2, col3, col4 = st.columns(4)
        
        # KPIs
        clientes = requests.get("http://localhost:8000/clientes/").json()
        mascotas = requests.get("http://localhost:8000/mascotas/").json()
        tratamientos = requests.get("http://localhost:8000/tratamientos/").json()
        citas = requests.get("http://localhost:8000/citas/").json()
        
        with col1:
            st.metric("Total Clientes", len(clientes))
        with col2:
            st.metric("Total Mascotas", len(mascotas))
        with col3:
            st.metric("Tratamientos Activos", len([t for t in tratamientos if t['estado'] == 'Activo']))
        with col4:
            citas_pendientes = len([c for c in citas if c['estado'] == 'Pendiente'])
            st.metric("Citas Pendientes", citas_pendientes)
        
        # Gráficos de resumen
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución de mascotas por estado
            df_mascotas = pd.DataFrame(mascotas)
            fig = px.pie(df_mascotas, names='estado', title='Estado de Mascotas')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Evolución de citas en el tiempo
            df_citas = pd.DataFrame(citas)
            df_citas['fecha'] = pd.to_datetime(df_citas['fecha'])
            fig = px.line(df_citas.groupby('fecha').size().reset_index(), 
                         x='fecha', y=0, title='Evolución de Citas')
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")

def show_analisis_clientes():
    st.header("Análisis de Clientes")
    
    try:
        clientes = requests.get("http://localhost:8000/clientes/").json()
        mascotas = requests.get("http://localhost:8000/mascotas/").json()
        
        # Distribución de edad de clientes
        df_clientes = pd.DataFrame(clientes)
        fig = px.histogram(df_clientes, x='edad', title='Distribución de Edad de Clientes',
                          nbins=20)
        st.plotly_chart(fig, use_container_width=True)
        
        # Clientes con más mascotas
        df_mascotas = pd.DataFrame(mascotas)
        mascotas_por_cliente = df_mascotas.groupby('id_cliente').size().reset_index()
        mascotas_por_cliente.columns = ['id_cliente', 'cantidad_mascotas']
        
        # Unir con datos de clientes
        df_clientes_mascotas = pd.merge(mascotas_por_cliente, df_clientes, on='id_cliente')
        fig = px.bar(df_clientes_mascotas.nlargest(10, 'cantidad_mascotas'),
                     x='nombre_cliente', y='cantidad_mascotas',
                     title='Top 10 Clientes por Número de Mascotas')
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")

def show_analisis_mascotas():
    st.header("Análisis de Mascotas")
    
    try:
        mascotas = requests.get("http://localhost:8000/mascotas/").json()
        df_mascotas = pd.DataFrame(mascotas)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución de razas
            fig = px.pie(df_mascotas, names='raza', title='Distribución de Razas')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Distribución de edades
            fig = px.histogram(df_mascotas, x='edad', title='Distribución de Edad de Mascotas')
            st.plotly_chart(fig, use_container_width=True)
        
        # Condiciones médicas más comunes
        if 'afeccion' in df_mascotas.columns:
            afecciones = df_mascotas['afeccion'].value_counts()
            fig = px.bar(afecciones, title='Condiciones Médicas Más Comunes')
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")

def show_analisis_tratamientos():
    st.header("Análisis de Tratamientos")
    
    try:
        tratamientos = requests.get("http://localhost:8000/tratamientos/").json()
        df_tratamientos = pd.DataFrame(tratamientos)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución de estados de tratamientos
            fig = px.pie(df_tratamientos, names='estado', 
                        title='Estado de Tratamientos')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Distribución de precios
            fig = px.box(df_tratamientos, y='precio', 
                        title='Distribución de Precios de Tratamientos')
            st.plotly_chart(fig, use_container_width=True)
        
        # Tratamientos más comunes
        tratamientos_comunes = df_tratamientos['nombre_tratamiento'].value_counts()
        fig = px.bar(tratamientos_comunes.head(10), 
                    title='Tratamientos Más Comunes')
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")

def show_analisis_citas():
    st.header("Análisis de Citas")
    
    try:
        citas = requests.get("http://localhost:8000/citas/").json()
        df_citas = pd.DataFrame(citas)
        df_citas['fecha'] = pd.to_datetime(df_citas['fecha'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Estado de citas
            fig = px.pie(df_citas, names='estado', 
                        title='Estado de Citas')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Citas por día de la semana
            df_citas['dia_semana'] = df_citas['fecha'].dt.day_name()
            citas_por_dia = df_citas['dia_semana'].value_counts()
            fig = px.bar(citas_por_dia, title='Citas por Día de la Semana')
            st.plotly_chart(fig, use_container_width=True)
            
        # Tendencia de citas en el tiempo
        citas_por_fecha = df_citas.groupby('fecha').size().reset_index()
        fig = px.line(citas_por_fecha, x='fecha', y=0, 
                     title='Evolución de Citas en el Tiempo')
        st.plotly_chart(fig, use_container_width=True)
        
        # Métodos de pago más utilizados
        if 'metodo_pago' in df_citas.columns:
            pagos = df_citas['metodo_pago'].value_counts()
            fig = px.pie(values=pagos.values, names=pagos.index, 
                        title='Métodos de Pago Utilizados')
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")