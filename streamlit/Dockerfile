FROM python:3.10-slim

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
    && apt-get clean

# Crear directorio de trabajo
WORKDIR /app

# Copiar los archivos desde la raíz del proyecto al contenedor
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# RUN python database.py

# Exponer el puerto de Streamlit
EXPOSE 8501

# Ejecutar Streamlit
CMD ["streamlit", "run", "main.py"]
