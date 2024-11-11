from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

# ========================
# Cliente Schemas
# ========================

class ClienteBase(BaseModel):
    nombre_cliente: str = Field(..., max_length=100)
    edad: int = Field(..., ge=0, le=120)
    dni: str = Field(..., min_length=9, max_length=9)
    direccion: str
    telefono: str = Field(..., min_length=9, max_length=15)

    @field_validator("dni")
    def validar_dni(cls, value):
        if not value.isalnum():
            raise ValueError("El DNI debe ser alfanumérico.")
        return value

    @field_validator("telefono")
    def validar_telefono(cls, value):
        if not value.isdigit():
            raise ValueError("El teléfono debe contener solo números.")
        return value

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(BaseModel):
    nombre_cliente: Optional[str]
    edad: Optional[int]
    dni: Optional[str]
    direccion: Optional[str]
    telefono: Optional[str]

class ClienteResponse(ClienteBase):
    id_cliente: int

    @classmethod
    def model_validate(cls, obj):
        return cls.model_construct(**{key: getattr(obj, key) for key in cls.__annotations__.keys()})

    model_config = ConfigDict(from_attributes=True)

# ========================
# Mascota Schemas
# ========================

class MascotaBase(BaseModel):
    nombre_mascota: str = Field(..., max_length=100)
    raza: str
    edad: int
    afeccion: Optional[str] = None
    estado: Optional[str] = "Vivo"
    id_cliente: int

    @field_validator("estado")
    def validar_estado(cls, value):
        estados_validos = ["Vivo", "Fallecido"]
        if value not in estados_validos:
            raise ValueError(f"El estado debe ser uno de {estados_validos}.")
        return value

class MascotaCreate(MascotaBase):
    pass

class MascotaUpdate(BaseModel):
    nombre_mascota: Optional[str]
    raza: Optional[str]
    edad: Optional[int]
    afeccion: Optional[str]
    estado: Optional[str]

class MascotaResponse(MascotaBase):
    id_mascota: int

    @classmethod
    def model_validate(cls, obj):
        return cls.model_construct(**{key: getattr(obj, key) for key in cls.__annotations__.keys()})

    model_config = ConfigDict(from_attributes=True)

# ========================
# Cita Schemas
# ========================

class CitaBase(BaseModel):
    fecha: datetime
    descripcion: str
    id_mascota: int
    id_cliente: int
    id_tratamiento: int

class CitaCreate(CitaBase):
    pass

class CitaUpdate(BaseModel):
    fecha: Optional[datetime]
    descripcion: Optional[str]

class CitaResponse(CitaBase):
    id_cita: int

    @classmethod
    def model_validate(cls, obj):
        return cls.model_construct(**{key: getattr(obj, key) for key in cls.__annotations__.keys()})

    model_config = ConfigDict(from_attributes=True)

# ========================
# Producto Schemas
# ========================

class ProductoBase(BaseModel):
    nombre_producto: str = Field(..., max_length=100)
    tipo_producto: str
    descripcion_producto: Optional[str] = None
    precio_producto: float = Field(..., gt=0)

    @field_validator("precio_producto")
    def validar_precio(cls, value):
        if value <= 0:
            raise ValueError("El precio debe ser mayor que 0.")
        return value

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(BaseModel):
    nombre_producto: Optional[str]
    tipo_producto: Optional[str]
    descripcion_producto: Optional[str]
    precio_producto: Optional[float]

class ProductoResponse(ProductoBase):
    id_producto: int

    @classmethod
    def model_validate(cls, obj):
        return cls.model_construct(**{key: getattr(obj, key) for key in cls.__annotations__.keys()})

    model_config = ConfigDict(from_attributes=True)

# ========================
# Tratamiento Schemas
# ========================

class TratamientoBase(BaseModel):
    nombre_tratamiento: str = Field(..., max_length=100)
    descripcion: str
    precio: float = Field(..., gt=0)
    id_cliente: int

    @field_validator("precio")
    def validar_precio(cls, value):
        if value <= 0:
            raise ValueError("El precio debe ser mayor que 0.")
        return value

class TratamientoCreate(TratamientoBase):
    pass

class TratamientoUpdate(BaseModel):
    nombre_tratamiento: Optional[str]
    descripcion: Optional[str]
    precio: Optional[float]
    id_cliente: Optional[int]

class TratamientoResponse(TratamientoBase):
    id_tratamiento: int

    @classmethod
    def model_validate(cls, obj):
        return cls.model_construct(**{key: getattr(obj, key) for key in cls.__annotations__.keys()})

    model_config = ConfigDict(from_attributes=True)
