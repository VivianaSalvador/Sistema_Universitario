from fastapi.testclient import TestClient
from main import app
from database import engine
from sqlalchemy import text
import pytest

client=TestClient(app)
M='Ingeniería de Software'
@pytest.fixture(autouse=True)
def limpiar():
    with engine.begin() as c:
        c.execute(text("DELETE FROM solicitudes"))
        c.execute(text("DELETE FROM usuarios WHERE codigo='A011'"))
        c.execute(text("UPDATE notas SET nota=90 WHERE alumno='A001'"))
    yield

def auth(code='A001', clave='Demo1234'):
    r=client.post('/login',json={'codigo':code,'clave':clave}); assert r.status_code==200
    return {'Authorization':r.json()['token']}

def nota(n, h=None):
    return client.put('/calificaciones',headers=h or auth('D001'),json={'alumno':'A001','materia':M,'nota':n})

def test_CP01_login(): assert auth()
def test_CP02_clave_incorrecta(): assert client.post('/login',json={'codigo':'A001','clave':'Incorrecta'}).status_code==401
def test_CP03_codigo_vacio(): assert client.post('/login',json={'codigo':' ','clave':'Demo1234'}).status_code==422
def test_CP04_materias(): assert client.get('/materias',headers=auth()).json()==[{'materia':M}]
def test_CP05_calificaciones(): assert client.get('/calificaciones',headers=auth()).json()==[{'materia':M,'nota':90}]
def test_CP06_adeudos(): assert client.get('/adeudos',headers=auth()).json()==[{'monto':150}]
def test_CP07_solicitud_seguimiento():
    h=auth(); r=client.post('/solicitudes',headers=h,json={'tipo':'Constancia'}); assert r.status_code==200
    assert {'folio':r.json()['folio'],'tipo':'Constancia','estado':'Pendiente'} in client.get('/solicitudes',headers=h).json()
def test_CP08_solicitud_vacia(): assert client.post('/solicitudes',headers=auth(),json={'tipo':'   '}).status_code==422
def test_CP09_grupos(): assert client.get('/grupos',headers=auth('D001')).json()==[{'alumno':'A001','materia':M,'nota':90}]
def test_CP10_nota_minima(): assert nota(0).status_code==200
def test_CP11_nota_maxima(): assert nota(100).status_code==200
def test_CP12_nota_negativa(): assert nota(-1).status_code==422
def test_CP13_nota_excesiva(): assert nota(101).status_code==422
def test_CP14_nota_booleana():
    r=nota(True); assert r.status_code==422, f'HTTP {r.status_code}: {r.json()}'
def test_CP15_integracion_nota():
    assert nota(95).status_code==200
    assert client.get('/calificaciones',headers=auth()).json()[0]['nota']==95
    assert client.get('/reportes',headers=auth('D001')).json()[0]['promedio']==95

def test_CP16_alumno_sin_permiso(): assert nota(80,auth()).status_code==403
def test_CP17_alta_y_login():
    r=client.post('/estudiantes',headers=auth('P001'),json={'codigo':'A011','nombre':'Estudiante prueba','clave':'Demo1234'}); assert r.status_code==200; assert auth('A011')
def test_CP18_duplicado(): assert client.post('/estudiantes',headers=auth('P001'),json={'codigo':'A001','nombre':'Otro','clave':'Demo1234'}).status_code==409
def test_CP19_logout():
    h=auth(); r=client.post('/logout',headers=h); assert r.status_code==200, f'HTTP {r.status_code}: {r.json()}'
    assert client.get('/materias',headers=h).status_code==401

def test_CP20_sin_sesion(): assert client.get('/materias').status_code==401
