from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from clinica.dbconfig import Base

 

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

    def to_dict(self):
        return {
            'id_mascota': self.id_mascota,
            'nombre_mascota': self.nombre_mascota,
            'raza': self.raza,
            'edad': self.edad,
            'afeccion': self.afeccion,
            'estado': self.estado
        }
