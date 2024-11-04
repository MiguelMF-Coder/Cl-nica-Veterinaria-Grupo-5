from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from dbconfig import Base

class Producto(Base):
    __tablename__ = "producto"

    id_producto = Column(Integer, primary_key=True, index=True)
    nombre_producto = Column(String, index=True)
    tipo_producto = Column(String)
    descripcion_producto = Column(String)
    precio_producto = Column(Integer)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente"))

    # Relaciones
    cliente = relationship("Cliente", back_populates="productos")
