import streamlit as st
import requests
from datetime import datetime

# URL del microservicio FastAPI
url = "http://fastapi:8000/envio/"

st.title("Ejemplo: formulario para dar la entrada de datos 🖥️🖥")

# Crear el formulario
with st.form("envio"):
    date = st.date_input("Fecha", datetime.now())
    description = st.text_input("Descripción")
    option = st.selectbox("Opción", ["Opción 1", "Opción 2", "Opción 3"])
    amount = st.number_input("Cantidad Económica", min_value=0.0, step=0.01)

    submit_button = st.form_submit_button(label="Enviar")

if submit_button:
    date_str = date.strftime("%Y-%m-%d")

    # Crear el payload para enviar al microservicio
    payload = {
        "date": date_str,
        "description": description,
        "option": option,
        "amount": amount
    }

    # Enviar los datos al microservicio usando requests
    response = requests.post(url, json=payload)

    # Mostrar el resultado de la solicitud
    if response.status_code == 200:
        st.success("Datos enviados correctamente")
        st.json(response.json())
    else:
        st.error("Error al enviar los datos")
