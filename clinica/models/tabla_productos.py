# models/productos.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from clinica.database import Base

class productos(Base):
    __tablename__ = "productos"

    id_producto = Column(Integer, primary_key=True, index=True)
    nombre_producto = Column(String, index=True)
    tipo_producto = Column(String)
    descripcion_producto = Column(String)
    precio_producto = Column(Integer)
    cliente_id = Column(Integer, ForeignKey("cliente.id_cliente"))

    #Relaciones:
    cliente = relationship("cliente", back_populates="productos")

