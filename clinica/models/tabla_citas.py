from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from clinica.dbconfig import Base

class Cita(Base):
    __tablename__ = "cita"

    id_cita = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime)
    descripcion = Column(String)
    id_mascota = Column(Integer, ForeignKey("mascota.id_mascota"))
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"))
    id_tratamiento = Column(Integer, ForeignKey("tratamiento.id_tratamiento"))

    # Relaciones
    mascota = relationship("Mascota", back_populates="citas")
    cliente = relationship("Cliente", back_populates="citas")
    tratamiento = relationship("Tratamiento", back_populates="citas")

    def to_dict(self):
        return {
            'id_cita': self.id_cita,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'descripcion': self.descripcion,
            'id_mascota': self.id_mascota,
            'id_cliente': self.id_cliente,
            'id_tratamiento': self.id_tratamiento
        }
