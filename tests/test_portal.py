from fastapi.testclient import TestClient
from main import app
from database import consultar
client=TestClient(app)
def auth(codigo):
    r=client.post('/login',json={'codigo':codigo,'clave':'Demo1234'}); assert r.status_code==200; return {'Authorization':r.json()['token']}
def test_login(): assert auth('A001')
def test_login_incorrecto(): assert client.post('/login',json={'codigo':'A001','clave':'Incorrecta'}).status_code==401
def test_calificaciones(): assert client.get('/calificaciones',headers=auth('A001')).json()[0]['nota']==90
def test_nota_invalida(): assert client.put('/calificaciones',headers=auth('D001'),json={'alumno':'A001','materia':'Ingeniería de Software','nota':101}).status_code==422
def test_solicitud():
    h=auth('A001'); r=client.post('/solicitudes',headers=h,json={'tipo':'Constancia'}); assert r.status_code==200; assert any(x['folio']==r.json()['folio'] for x in client.get('/solicitudes',headers=h).json())
def test_duplicado(): assert client.post('/estudiantes',headers=auth('P001'),json={'codigo':'A001','nombre':'Otro','clave':'Demo1234'}).status_code==409
def test_permiso(): assert client.get('/grupos',headers=auth('A001')).status_code==403
def test_sin_sesion(): assert client.get('/materias').status_code==401
def test_titulo_vacio(): assert client.post('/solicitudes',headers=auth('A001'),json={'tipo':'   '}).status_code==422
def test_hash(): assert ':' in consultar('SELECT clave FROM usuarios WHERE codigo=:c',c='A001')[0]['clave']
def test_actualizar_nota():
    assert client.put('/calificaciones',headers=auth('D001'),json={'alumno':'A001','materia':'Ingeniería de Software','nota':95}).status_code==200
    assert client.get('/calificaciones',headers=auth('A001')).json()[0]['nota']==95
