#Tabla_tratamiento

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from clinica.dbconfig import Base


class Tratamiento(Base):
    __tablename__ = "tratamiento"

    id_tratamiento = Column(Integer, primary_key=True, index=True)
    nombre_tratamiento = Column(String, index=True)
    descripcion = Column(String)
    precio = Column(Integer)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"))

    # Relaciones
    cliente = relationship("Cliente", back_populates="tratamientos")
