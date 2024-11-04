from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from dbconfig import Base

class Cita(Base):
    __tablename__ = "cita"

    id_cita = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime)
    descripcion = Column(String)
    id_mascota = Column(Integer, ForeignKey("mascota.id_mascota"))
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"))

    # Relaciones
    mascota = relationship("Mascota", back_populates="citas")
    cliente = relationship("Cliente", back_populates="citas")
