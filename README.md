# Portal universitario · Tarea 10
Demostración académica local con datos ficticios. En PowerShell, desde esta carpeta:

    python -m venv .venv
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    .\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000

Abrir http://127.0.0.1:8000 o /docs. Detener con Ctrl+C.
Pruebas: `.\.venv\Scripts\python.exe -m pytest -q`.
Git: `git log --oneline --stat` (el ZIP incluye .git). Datos demo A001 estudiante, D001 docente, P001 administrativo, S001 administrador; clave Demo1234. No usar datos reales ni exponer el servidor a Internet. La base SQLite se crea automáticamente. PostgreSQL es una alternativa no verificada aquí: definir DATABASE_URL con URL SQLAlchemy postgresql+psycopg hacia una base vacía. Sesiones en memoria; se invalidan al reiniciar. El modelo de datos es una simplificación de las tareas previas, no un sistema de producción. Para producción faltan integración institucional, caducidad de sesiones, TLS, auditoría, gestión completa de grupos y trámites y pruebas de carga.

## Tarea 11
Ejecutar `python -m pytest -v` para las 31 pruebas (20 nuevas y 11 de regresión). Se usa una base temporal separada de la aplicación. Los casos CP14 y CP19 comprueban el rechazo de booleanos y la revocación del token. Para repetir solo estos: `python -m pytest -v tests/test_tarea11.py -k "CP14 or CP19"`. Los registros de ejecución antes/después están en Evidencias del entregable. Las cuentas y el servidor son solo de demostración local.
