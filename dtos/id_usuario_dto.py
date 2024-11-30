from pydantic import BaseModel, field_validator

from util.validators import *


class IdClienteDto(BaseModel):
    id_usuario: int

    @field_validator("id_usuario")
    def validar_id_usuario(cls, v):
        msg = is_greater_than(v, "Id do Usuario", 0)
        if msg: raise ValueError(msg)
        return v