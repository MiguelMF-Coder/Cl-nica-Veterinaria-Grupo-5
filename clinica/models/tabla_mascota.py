# models/mascota.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from clinica.database import Base

class Mascota(Base):
    __tablename__ = "mascota"

    id_mascota = Column(Integer, primary_key=True, index=True)
    nombre_mascota = Column(String, index=True)
    raza = Column(String)
    edad = Column(Integer)
    afeccion = Column(String)
    Estado = Column(String)
    cliente_id = Column(Integer, ForeignKey("cliente.id_cliente"))

    #Relaciones:
    cliente = relationship("cliente", back_populates="mascotas")
    citas = relationship("Cita", back_populates="mascotas")