# Usa una imagen base de Python para mayor flexibilidad
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
    libssl-dev \
    libffi-dev \
    && apt-get clean

# Establece una variable de entorno para evitar crear archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crea y establece el directorio de trabajo
WORKDIR /app

RUN pip install --no-cache-dir uvicorn

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación
COPY . .


# Expone el puerto 8000 para la aplicación
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
