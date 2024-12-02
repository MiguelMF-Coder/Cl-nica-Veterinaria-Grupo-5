FROM python:3.10-slim

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    libwebp-dev \
    build-essential \
    make \
    libpng-dev \
    libxrender1 \
    libxext6 \
    libatlas-base-dev \
    libssl-dev \
    libffi-dev \
    && apt-get clean

# Crear directorio de trabajo
WORKDIR /app

# Copiar los archivos de la aplicación al contenedor
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Establecer la variable PYTHONPATH para incluir /app
ENV PYTHONPATH="/app"

# Exponer el puerto de Streamlit
EXPOSE 8501

# Comando de inicio que ejecuta database.py antes de iniciar Streamlit
CMD ["sh", "-c", "streamlit run main.py"]
