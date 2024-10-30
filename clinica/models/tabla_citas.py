# models/citas.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base

class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime)  
    descripcion = Column(String)  
    mascota_id = Column(Integer, ForeignKey("id.mascotas")) 
    cliente_id = Column(Integer, ForeignKey("id.cliente"))  

    # Relaciones:
    mascota = relationship("Mascota", back_populates="citas")
    cliente = relationship("Cliente", back_populates="citas")

