# models/tratamientos.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from clinica.database import Base

class tratamientos(Base):
    __tablename__ = "tratamientos"

    id_tratamiento = Column(Integer, primary_key=True, index=True)
    nombre_tratamiento = Column(String, index=True)
    descripcion = Column(String)
    precio = Column(Integer)
    cliente_id = Column(Integer, ForeignKey("cliente.id_cliente"))

    #Relación:
    cliente = relationship("cliente", back_populates="tratamientos")
