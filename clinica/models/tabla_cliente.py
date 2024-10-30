# models/cliente.py
from sqlalchemy import Column, Integer, String, ForeignKey
from .database import Base

class cliente(Base):
    __tablename__ = "cliente"

    id_cliente = Column(Integer, primary_key=True, index=True)
    nombre_cliente = Column(String, index=True)
    edad = Column(Integer)
    dni = Column(String)
    dirección = Column(Integer)
    telefono = Column(Integer)
    id_mascota = Column(Integer, ForeignKey("id.mascota"))

    #Relaciones:
    mascotas = relationship("Mascota", back_populates="cliente")
    citas = relationship("Cita", back_populates="cliente")
    tratamientos = relationship("Tratamiento", back_populates="cliente")
    productos = relationship("Producto", back_populates="cliente")
