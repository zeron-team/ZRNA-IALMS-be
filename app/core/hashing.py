import bcrypt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña plana contra un hash usando bcrypt directamente.
    """
    try:
        # bcrypt necesita que ambos argumentos sean bytes
        plain_password_bytes = plain_password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')

        return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
    except Exception:
        # Si hay cualquier error (ej: hash malformado), la verificación falla
        return False


def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña usando bcrypt directamente.
    """
    password_bytes = password.encode('utf-8')
    # Genera una 'salt' y la incluye en el hash
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    # Devuelve el hash como un string para guardarlo en la base de datos
    return hashed_bytes.decode('utf-8')