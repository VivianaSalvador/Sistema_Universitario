from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import text
from database import engine, iniciar
from pathlib import Path
import secrets
app=FastAPI(title='Portal universitario')
iniciar()
sesiones={}
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

def usuario(authorization):
    u=sesiones.get(authorization or '')
    if not u: raise HTTPException(401,'Inicia sesión')
    return u

def permiso(u,*roles):
    if u['rol'] not in roles: raise HTTPException(403,'Sin permiso')

def consultar(sql,**params):
    with engine.connect() as c: return [dict(r) for r in c.execute(text(sql),params).mappings()]

@app.get('/')
def inicio(): return FileResponse(Path(__file__).parent/'index.html')
@app.post('/login')
def login(d:Login):
    filas=consultar('SELECT * FROM usuarios WHERE codigo=:c AND clave=:p',c=d.codigo,p=d.clave)
    if not filas: raise HTTPException(401,'Credenciales incorrectas')
    u={k:filas[0][k] for k in ('codigo','nombre','rol')}; token=secrets.token_urlsafe(32); sesiones[token]=u
    return dict(token=token,**u)
@app.get('/materias')
def materias(authorization:str|None=Header(None)):
    u=usuario(authorization); permiso(u,'estudiante'); return consultar('SELECT materia FROM notas WHERE alumno=:a',a=u['codigo'])
@app.get('/calificaciones')
def calificaciones(authorization:str|None=Header(None)):
    u=usuario(authorization); permiso(u,'estudiante'); return consultar('SELECT materia,nota FROM notas WHERE alumno=:a',a=u['codigo'])
@app.get('/adeudos')
def adeudos(authorization:str|None=Header(None)):
    u=usuario(authorization); permiso(u,'estudiante'); return consultar('SELECT monto FROM adeudos WHERE alumno=:a',a=u['codigo'])
@app.post('/solicitudes')
def solicitar(d:Solicitud,authorization:str|None=Header(None)):
    u=usuario(authorization); permiso(u,'estudiante'); folio=secrets.token_hex(8)
    with engine.begin() as c: c.execute(text('INSERT INTO solicitudes VALUES (:f,:a,:t,:e)'),dict(f=folio,a=u['codigo'],t=d.tipo,e='Pendiente'))
    return {'folio':folio,'estado':'Pendiente'}
@app.get('/solicitudes')
def solicitudes(authorization:str|None=Header(None)):
    u=usuario(authorization); permiso(u,'estudiante'); return consultar('SELECT folio,tipo,estado FROM solicitudes WHERE alumno=:a',a=u['codigo'])
@app.get('/grupos')
def grupos(authorization:str|None=Header(None)):
    u=usuario(authorization); permiso(u,'docente'); return consultar('SELECT alumno,materia,nota FROM notas WHERE docente=:d',d=u['codigo'])
@app.put('/calificaciones')
def registrar_nota(d:Nota,authorization:str|None=Header(None)):
    u=usuario(authorization); permiso(u,'docente')
    with engine.begin() as c:
        r=c.execute(text('UPDATE notas SET nota=:n WHERE alumno=:a AND materia=:m AND docente=:d'),dict(n=d.nota,a=d.alumno,m=d.materia,d=u['codigo']))
        if not r.rowcount: raise HTTPException(404,'Registro no encontrado')
    return {'mensaje':'Calificación actualizada'}
@app.get('/reportes')
def reportes(authorization:str|None=Header(None)):
    u=usuario(authorization); permiso(u,'docente','administrativo','admin')
    if u['rol']=='docente': return consultar('SELECT materia,COUNT(*) AS total,AVG(nota) AS promedio FROM notas WHERE docente=:d GROUP BY materia',d=u['codigo'])
    return consultar('SELECT rol,COUNT(*) AS total FROM usuarios GROUP BY rol')
@app.post('/estudiantes')
def registrar(d:Alumno,authorization:str|None=Header(None)):
    u=usuario(authorization); permiso(u,'administrativo','admin')
    if consultar('SELECT codigo FROM usuarios WHERE codigo=:c',c=d.codigo): raise HTTPException(409,'Código duplicado')
    with engine.begin() as c: c.execute(text('INSERT INTO usuarios VALUES (:c,:n,:p,:r)'),dict(c=d.codigo,n=d.nombre,p=d.clave,r='estudiante'))
    return {'mensaje':'Estudiante registrado'}
