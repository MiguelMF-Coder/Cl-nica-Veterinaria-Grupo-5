# Usa una imagen base de Python para mayor flexibilidad
FROM python:3.10-slim

# Establece una variable de entorno para evitar crear archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crea y establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requisitos
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación
COPY . .

ENV PYTHONPATH=/app

# Expone el puerto 8000 para la aplicación
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
