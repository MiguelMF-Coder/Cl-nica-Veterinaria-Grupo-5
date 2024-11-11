from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from clinica.dbconfig import Base

class Cliente(Base):
    __tablename__ = "cliente"

    id_cliente = Column(Integer, primary_key=True, index=True)
    nombre_cliente = Column(String, index=True)
    edad = Column(Integer)
    dni = Column(String)
    direccion = Column(String)
    telefono = Column(Integer)

    # Relaciones
    mascotas = relationship("Mascota", back_populates="cliente")
    citas = relationship("Cita", back_populates="cliente")
    tratamientos = relationship("Tratamiento", back_populates="cliente")
    productos = relationship("Producto", back_populates="cliente")

    def to_dict(self):
        return {
            'id_cliente': self.id_cliente,
            'nombre_cliente': self.nombre_cliente,
            'edad': self.edad,
            'dni': self.dni,
            'direccion': self.direccion,
            'telefono': self.telefono
        }
