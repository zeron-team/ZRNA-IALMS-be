# backend/generate_hash.py
import sys
from app.core.hashing import get_password_hash

# Asegúrate de que el script pueda encontrar la carpeta 'app'
sys.path.append('.')

def main():
    password = input("Ingresa la contraseña para generar el hash: ")
    if not password:
        print("No se ingresó ninguna contraseña.")
        return

    hashed_password = get_password_hash(password)
    print("\n✅ Hash generado con éxito:")
    print(hashed_password)

if __name__ == "__main__":
    main()