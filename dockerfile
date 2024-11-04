# Usa una imagen base de Python
FROM python:3.10-slim

# Instala dependencias del sistema necesarias para paquetes como Pillow
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

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Establece la variable de entorno PYTHONPATH
ENV PYTHONPATH=/app

# Actualiza pip, setuptools y wheel
RUN pip install --upgrade pip setuptools wheel

# Instala las dependencias del archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto que usará tu aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["python3", "main.py"]
