"""Hash de contraseñas con sal individual y comparación constante."""
import hashlib, secrets, hmac

def hash_clave(clave):
    sal=secrets.token_hex(16)
    digest=hashlib.pbkdf2_hmac('sha256',clave.encode(),bytes.fromhex(sal),600000).hex()
    return sal+':'+digest

def verificar(clave, guardada):
    try:
        sal,digest=guardada.split(':',1)
        calculado=hashlib.pbkdf2_hmac('sha256',clave.encode(),bytes.fromhex(sal),600000).hex()
        return hmac.compare_digest(calculado,digest)
    except ValueError:
        return False
