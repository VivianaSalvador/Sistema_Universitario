import os
from pathlib import Path
from sqlalchemy import create_engine, text, event
from seguridad import hash_clave
URL = os.getenv('DATABASE_URL', 'sqlite:///' + str(Path(__file__).parent / 'universidad.db'))
engine = create_engine(URL, connect_args={'check_same_thread': False} if URL.startswith('sqlite') else {})

if URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def activar_fk(conn, _):
        conn.execute("PRAGMA foreign_keys=ON")

def iniciar():
    with engine.begin() as c:
        c.execute(text('CREATE TABLE IF NOT EXISTS usuarios (codigo VARCHAR(30) PRIMARY KEY, nombre VARCHAR(100) NOT NULL, clave VARCHAR(200) NOT NULL, rol VARCHAR(30) NOT NULL)'))
        c.execute(text('CREATE TABLE IF NOT EXISTS notas (alumno VARCHAR(30) REFERENCES usuarios(codigo), materia VARCHAR(100), docente VARCHAR(30) REFERENCES usuarios(codigo), nota FLOAT, PRIMARY KEY(alumno,materia))'))
        c.execute(text('CREATE TABLE IF NOT EXISTS solicitudes (folio VARCHAR(40) PRIMARY KEY, alumno VARCHAR(30) REFERENCES usuarios(codigo), tipo VARCHAR(100), estado VARCHAR(30))'))
        c.execute(text('CREATE TABLE IF NOT EXISTS adeudos (alumno VARCHAR(30) PRIMARY KEY REFERENCES usuarios(codigo), monto FLOAT)'))
        if not c.execute(text('SELECT codigo FROM usuarios')).first():
            for codigo,nombre,rol in [('A001','Ana García','estudiante'),('D001','Luis Pérez','docente'),('P001','Control escolar','administrativo'),('S001','Administrador','admin')]:
                c.execute(text('INSERT INTO usuarios VALUES (:c,:n,:p,:r)'),dict(c=codigo,n=nombre,p=hash_clave('Demo1234'),r=rol))
            c.execute(text("INSERT INTO notas VALUES ('A001','Ingeniería de Software','D001',90)"))
            c.execute(text("INSERT INTO adeudos VALUES ('A001',150)"))

        # Migrar las claves de la versión inicial sin borrar registros.
        for codigo, clave in c.execute(text("SELECT codigo,clave FROM usuarios")).all():
            if ":" not in clave:
                c.execute(text("UPDATE usuarios SET clave=:p WHERE codigo=:c"),dict(p=hash_clave(clave),c=codigo))

def consultar(sql,**params):
    with engine.connect() as c: return [dict(r) for r in c.execute(text(sql),params).mappings()]

