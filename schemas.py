from pydantic import BaseModel, Field, ConfigDict

class Datos(BaseModel):
    model_config=ConfigDict(str_strip_whitespace=True)
class Login(Datos):
    codigo:str=Field(min_length=1,max_length=30)
    clave:str=Field(min_length=8,max_length=100)
class Nota(Datos):
    alumno:str=Field(min_length=1,max_length=30)
    materia:str=Field(min_length=1,max_length=100)
    nota:float=Field(ge=0,le=100,allow_inf_nan=False)
class Solicitud(Datos):
    tipo:str=Field(min_length=1,max_length=100)
class Alumno(Datos):
    codigo:str=Field(min_length=1,max_length=30)
    nombre:str=Field(min_length=1,max_length=100)
    clave:str=Field(min_length=8,max_length=100)

