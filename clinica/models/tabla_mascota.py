# models/mascota.py
from sqlalchemy import Column, Integer, String, ForeignKey
from .database import Base

class Mascota(Base):
    __tablename__ = "mascotas"

    id_mascota = Column(Integer, primary_key=True, index=True)
    nombre_mascota = Column(String, index=True)
    raza = Column(String)
    edad = Column(Integer)
    afeccion = Column(String)
    Estado = Column(String)
    cliente_id = Column(Integer, ForeignKey("id.cliente"))

    #Relaciones:
    cliente = relationship("Cliente", back_populates="mascotas")
    citas = relationship("Cita", back_populates="mascota")