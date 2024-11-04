from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from dbconfig import Base

class Mascota(Base):
    __tablename__ = "mascota"

    id_mascota = Column(Integer, primary_key=True, index=True)
    nombre_mascota = Column(String, index=True)
    raza = Column(String)
    edad = Column(Integer)
    afeccion = Column(String)
    estado = Column(String)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"))

    # Relaciones
    cliente = relationship("Cliente", back_populates="mascotas")
    citas = relationship("Cita", back_populates="mascota")
