# Usamos una imagen Python 3
FROM python:3

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de tu proyecto al contenedor
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto que usará tu aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["python3", "clinica/main.py"]
