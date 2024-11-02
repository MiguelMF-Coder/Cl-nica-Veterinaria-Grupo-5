FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar los archivos desde la raíz del proyecto al contenedor
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

RUN python init_db.py

# Exponer el puerto de Streamlit
EXPOSE 8501

# Ejecutar Streamlit
CMD ["streamlit", "run", "main.py"]
