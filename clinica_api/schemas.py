from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

# ========================
# Cliente Schemas
# ========================

class ClienteBase(BaseModel):
    nombre_cliente: str = Field(..., min_length=2, max_length=100, description="Nombre completo del cliente")
    edad: int = Field(..., ge=0, le=120, description="Edad del cliente")
    dni: str = Field(..., min_length=9, max_length=9, description="DNI del cliente")
    direccion: str = Field(..., min_length=5, max_length=200, description="Dirección completa del cliente")
    telefono: str = Field(..., min_length=9, max_length=15, description="Número de teléfono del cliente", strict=True)


    @field_validator("dni")
    @classmethod
    def validar_dni(cls, value: str) -> str:
        if not (value[:-1].isdigit() and value[-1].isalpha()):
            raise ValueError("El DNI debe tener 8 números seguidos de una letra")
        return value.upper()

    
    @field_validator("telefono", mode="before")
    @classmethod
    def validar_telefono(cls, value) -> str:
        # Convertir el valor a string si es un entero
        if isinstance(value, int):
            value = str(value)
        if not value.isdigit():
            raise ValueError("El teléfono debe contener solo números")
        if not value.startswith(('6', '7', '9')):
            raise ValueError("El teléfono debe empezar por 6, 7 o 9")
        return value


    class Config:
        from_attributes = True

class ClienteCreate(ClienteBase):
    model_config = ConfigDict(from_attributes=True)

class ClienteUpdate(BaseModel):
    nombre_cliente: Optional[str] = Field(None, min_length=2, max_length=100)
    edad: Optional[int] = Field(None, ge=0, le=120)
    dni: Optional[str] = Field(None, min_length=9, max_length=9)
    direccion: Optional[str] = Field(None, min_length=5, max_length=200)
    telefono: Optional[str] = Field(None, min_length=9, max_length=15)

    model_config = ConfigDict(from_attributes=True)

class ClienteResponse(ClienteBase):
    id_cliente: int = Field(..., description="ID único del cliente")
    
    model_config = ConfigDict(from_attributes=True)

# ========================
# Mascota Schemas
# ========================

class MascotaBase(BaseModel):
    nombre_mascota: str = Field(..., min_length=2, max_length=100, description="Nombre de la mascota")
    raza: str = Field(..., min_length=2, max_length=100, description="Raza de la mascota")
    edad: int = Field(..., ge=0, le=50, description="Edad de la mascota")
    afeccion: Optional[str] = Field(None, max_length=500, description="Afección o condición médica")
    estado: str = Field("Vivo", description="Estado actual de la mascota")
    id_cliente: int = Field(..., gt=0, description="ID del cliente propietario")

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value: str) -> str:
        estados_validos = ["Vivo", "Fallecido"]
        if value not in estados_validos:
            raise ValueError(f"Estado debe ser uno de: {', '.join(estados_validos)}")
        return value

class MascotaCreate(MascotaBase):
    model_config = ConfigDict(from_attributes=True)

class MascotaUpdate(BaseModel):
    nombre_mascota: Optional[str] = Field(None, min_length=2, max_length=100)
    raza: Optional[str] = Field(None, min_length=2, max_length=100)
    edad: Optional[int] = Field(None, ge=0, le=50)
    afeccion: Optional[str] = Field(None, max_length=500)
    estado: Optional[str] = Field(None)

    model_config = ConfigDict(from_attributes=True)

class MascotaResponse(MascotaBase):
    id_mascota: int = Field(..., description="ID único de la mascota")
    
    model_config = ConfigDict(from_attributes=True)

# ========================
# Cita Schemas
# ========================

class CitaBase(BaseModel):
    fecha: datetime = Field(..., description="Fecha y hora de la cita")
    descripcion: str = Field(..., min_length=10, max_length=500, description="Descripción de la cita")
    estado: str = Field("Pendiente", description="Estado de la cita")
    id_mascota: int = Field(..., gt=0, description="ID de la mascota")
    id_cliente: int = Field(..., gt=0, description="ID del cliente")
    id_tratamiento: int = Field(..., gt=0, description="ID del tratamiento")
    metodo_pago: Optional[str] = Field(None, description="Método de pago utilizado")

    @field_validator("estado")
    @classmethod
    def validar_estado_cita(cls, value: str) -> str:
        estados_validos = ["Pendiente", "Confirmada", "En Proceso", "Finalizada", "Cancelada"]
        if value not in estados_validos:
            raise ValueError(f"Estado '{value}' no es válido. Debe ser uno de: {', '.join(estados_validos)}")
        return value

    @field_validator("metodo_pago")
    @classmethod
    def validar_metodo_pago(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        metodos_validos = ["Efectivo", "Tarjeta", "Bizum", "Transferencia"]
        if value not in metodos_validos:
            raise ValueError(f"Método de pago '{value}' no es válido. Debe ser uno de: {', '.join(metodos_validos)}")
        return value

class CitaCreate(CitaBase):
    model_config = ConfigDict(from_attributes=True)

class CitaUpdate(BaseModel):
    fecha: Optional[datetime] = None
    descripcion: Optional[str] = Field(None, min_length=10, max_length=500)
    estado: Optional[str] = None
    metodo_pago: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("estado")
    @classmethod
    def validar_estado_cita(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        estados_validos = ["Pendiente", "Confirmada", "En Proceso", "Finalizada", "Cancelada"]
        if value not in estados_validos:
            raise ValueError(f"Estado '{value}' no es válido. Debe ser uno de: {', '.join(estados_validos)}")
        return value

    @field_validator("metodo_pago")
    @classmethod
    def validar_metodo_pago(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        metodos_validos = ["Efectivo", "Tarjeta", "Bizum", "Transferencia"]
        if value not in metodos_validos:
            raise ValueError(f"Método de pago '{value}' no es válido. Debe ser uno de: {', '.join(metodos_validos)}")
        return value

class CitaResponse(CitaBase):
    id_cita: int = Field(..., description="ID único de la cita")
    
    model_config = ConfigDict(from_attributes=True)

# ========================
# Tratamiento Schemas
# ========================

class TratamientoBase(BaseModel):
    nombre_tratamiento: str = Field(..., min_length=2, max_length=100, description="Nombre del tratamiento")
    descripcion: str = Field(..., min_length=10, max_length=500, description="Descripción del tratamiento")
    precio: float = Field(..., gt=0, description="Precio del tratamiento")
    estado: str = Field("Activo", description="Estado del tratamiento")
    id_cliente: int = Field(..., gt=0, description="ID del cliente")

    @field_validator("estado")
    @classmethod
    def validar_estado_tratamiento(cls, value: str) -> str:
        estados_validos = ["Activo", "Finalizada", "Cancelada"]
        if value not in estados_validos:
            raise ValueError(f"Estado debe ser uno de: {', '.join(estados_validos)}")
        return value

class TratamientoCreate(TratamientoBase):
    model_config = ConfigDict(from_attributes=True)

class TratamientoUpdate(BaseModel):
    nombre_tratamiento: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, min_length=10, max_length=500)
    precio: Optional[float] = Field(None, gt=0)
    estado: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class TratamientoResponse(TratamientoBase):
    id_tratamiento: int = Field(..., description="ID único del tratamiento")
    
    model_config = ConfigDict(from_attributes=True)