import mysql.connector
from mysql.connector import errorcode
import bcrypt
from config import *

# Códigos ANSI para colores
COLOR_RED = '\033[91m'
COLOR_GREEN = '\033[92m'
COLOR_YELLOW = '\033[93m'
COLOR_END = '\033[0m'

def validar_nombre(nombre):
    if len(nombre) > 30 or not nombre.isalpha():
        return False
    return True

def validar_email(email):
    # Esta expresión regular verifica que el input sea un correo electrónico válido
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def validar_usuario(usuario):
    if len(usuario) > 30 or not usuario.isalpha():
        return False
    return True

def insert_admin(username, password, email, full_name):
    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        cursor = conn.cursor()

        # Generar un hash de la contraseña usando bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Inserción del usuario administrador con contraseña cifrada
        insert_query = """
        INSERT INTO admin (username, password, email, full_name) VALUES (%s, %s, %s, %s)
        """
        data = (username, hashed_password.decode('utf-8'), email, full_name)
        cursor.execute(insert_query, data)
        conn.commit()
        print(f"{COLOR_GREEN}[*] Usuario administrador creado exitosamente ...{COLOR_END}")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print(f"{COLOR_RED}[x] Error: Acceso denegado{COLOR_END}")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"{COLOR_RED}[x] Error: Base de datos no existe{COLOR_END}")
        else:
            print(f"{COLOR_RED}[x] Error: {err}{COLOR_END}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    # pedir la el usuario y contraseña
    print(f"{COLOR_YELLOW}[!] recuerde que estos datos serán usados para iniciar sesión en el panel de Administración)..{COLOR_END}\n")
    
    try:
        full_name = input("[*] Nombre Completo: ")
        if not validar_nombre(full_name):
            print("Nombre demasiado largo o contiene caracteres no permitidos. Máximo 10 caracteres y solo letras.")
            exit()

        email = input("[*] Correo Electronico: ")
        if not validar_email(email):
            print("Correo electrónico no válido.")
            exit()

        username = input("[*] Usuario: ")
        if not validar_usuario(username):
            print("Usuario demasiado largo o contiene caracteres no permitidos. Máximo 10 caracteres y solo letras.")
            exit()

        password = input("[*] Contraseña: ")
        insert_admin(username, password, email, full_name)
    except KeyboardInterrupt:
        print(f"\n{COLOR_YELLOW}[!] Saliendo...{COLOR_END}")

