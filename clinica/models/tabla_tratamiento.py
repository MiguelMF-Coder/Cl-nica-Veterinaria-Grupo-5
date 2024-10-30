# models/tratamientos.py
from sqlalchemy import Column, Integer, String, ForeignKey
from .database import Base

class tratamientos(Base):
    __tablename__ = "tratamientos"

    id_tratamiento = Column(Integer, primary_key=True, index=True)
    nombre_tratamiento = Column(String, index=True)
    descripcion = Column(String)
    precio = Column(Integer)
    cliente_id = Column(Integer, ForeignKey("id.cliente"))

    #Relación:
    cliente = relationship("Cliente", back_populates="tratamientos")
