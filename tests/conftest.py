# Siempre probar en una base temporal, nunca en la base de la aplicación.
import os
import tempfile
from pathlib import Path
os.environ['DATABASE_URL'] = 'sqlite:///' + str(Path(tempfile.mkdtemp()) / 'test.db')
