# models/citas.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from clinica.database import Base

class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime)  
    descripcion = Column(String)  
    mascota_id = Column(Integer, ForeignKey("mascota.id_mascota")) 
    cliente_id = Column(Integer, ForeignKey("cliente.id_cliente"))  

    # Relaciones:
    mascota = relationship("mascota", back_populates="citas")
    cliente = relationship("cliente", back_populates="citas")

