from clinica.database import Base, engine
from sqlalchemy.exc import OperationalError
from sqlalchemy import inspect

def initialize_database():
    inspector = inspect(engine)
    # Si la tabla `tabla_cliente` no existe, inicializa la base de datos
    if not inspector.has_table("tabla_cliente"):
        Base.metadata.create_all(bind=engine)
        print("Tablas creadas exitosamente.")
    else:
        print("Las tablas ya existen. No se necesita inicialización.")

if __name__ == "__main__":
    initialize_database()
