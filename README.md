# Proyecto de Gestión de Clínica Veterinaria UFVVet

## Descripción
UFVVet es un sistema integral para la gestión de una clínica veterinaria, desarrollado utilizando FastAPI para el backend y Streamlit para el frontend. Este sistema permite gestionar clientes, mascotas, citas y tratamientos con una interfaz fácil de usar y funcionalidades avanzadas.

---

## Características Principales

### 1. Gestión de Clientes
- Registro, modificación, eliminación y búsqueda de clientes.
- Validación de datos como DNI y teléfono.
- Exportación de datos de clientes a archivos JSON.

### 2. Gestión de Mascotas
- Registro de mascotas vinculadas a clientes.
- Modificación y eliminación de mascotas.
- Visualización y búsqueda de mascotas.
- Exportación de datos de mascotas a archivos JSON.

### 3. Gestión de Citas
- Creación, modificación, cancelación y finalización de citas.
- Visualización interactiva de un calendario de citas.
- Generación automática de facturas en formato PDF al finalizar una cita.

### 4. Gestión de Tratamientos
- Registro de tratamientos y asociación a clientes.
- Modificación y eliminación de tratamientos.
- Visualización y búsqueda de tratamientos.
- Exportación de datos de tratamientos a archivos JSON.

### 5. Dashboard
- Panel de análisis con métricas clave como total de clientes, mascotas, citas y tratamientos.
- Gráficos interactivos que muestran tendencias y distribuciones de datos.

---

## Tecnologías Utilizadas

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Base de datos**: SQLite
- **Librerías**:
  - SQLAlchemy: para la gestión de la base de datos.
  - Pydantic: validación de datos y creación de esquemas.
  - ReportLab: generación de facturas en PDF.
  - Plotly: gráficos interactivos en el dashboard.

---

## Instalación y Configuración

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/MiguelMF-Coder/Cl-nica-Veterinaria-Grupo-5.git
   cd Cl-nica-Veterinaria-Grupo-5
   ```

2. **Ejecutar la aplicación con Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Acceso al sistema**:
   - **Frontend (Streamlit)**: [http://localhost:8501](http://localhost:8501)
   - **Backend (FastAPI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Arquitectura

- **FastAPI**:
  - Manejo de la lógica de negocio y las operaciones CRUD (clientes, mascotas, citas, tratamientos).
  - Endpoints RESTful documentados en Swagger.

- **Streamlit**:
  - Interfaz de usuario intuitiva con funcionalidades interactivas.
  - Organización en páginas para cada sección del sistema (Inicio, Clientes, Mascotas, Citas, Tratamientos, Dashboard).

---

## Contribución

1. Haz un fork del repositorio.
2. Crea una rama para tu función:
   ```bash
   git checkout -b nueva-funcionalidad
   ```
3. Realiza tus cambios y haz commits:
   ```bash
   git commit -m "Agrega nueva funcionalidad"
   ```
4. Envía un pull request.

---

## Licencia

Este proyecto está bajo la licencia MIT. Para más información, consulta el archivo LICENSE.

