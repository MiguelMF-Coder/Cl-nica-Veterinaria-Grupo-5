from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from clinica.dbconfig import Base



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

    def to_dict(self):
        return {
            'id_producto': self.id_producto,
            'nombre_producto': self.nombre_producto,
            'tipo_producto': self.tipo_producto,
            'descripcion_producto': self.descripcion_producto,
            'precio_producto': self.precio_producto,
            'id_cliente': self.id_cliente,
        }