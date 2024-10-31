from clinica.database import Base, engine
from clinica.models import tabla_citas, tabla_cliente, tabla_mascota, tabla_productos, tabla_tratamiento  # Importamos las tablas desde el modulo de modelos


# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)
print("Tablas creadas exitosamente.")
