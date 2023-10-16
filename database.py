## IMPORTS ##

import mysql.connector
from flask_bcrypt import Bcrypt
from config import DB_HOST,DB_NAME,DB_PASSWORD,DB_USER
from config import *

# necessary global variables
now = datetime.now()
time_stamp = now.strftime("%Y%H%M%S")

class DatabaseConnection:
    """
    Clase para inicializar la conexión a la base de datos
    """
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        self.cursor = self.conn.cursor()

class ShowProducts(DatabaseConnection):
    """
    Clase para mostrar productos desde la base de datos.
    """
    def __init__(self):
        super().__init__()
    
    def show(self):
        """
        Recupera y devuelve todos los productos desde la base de datos.

        Returns:
            list: Lista de productos, donde cada producto es un diccionario con sus atributos.
        """
        query = "SELECT * from productos"
        self.cursor.execute(query)

        products = self.cursor.fetchall()

        return products


# Pedidos
class ShowPedidos(DatabaseConnection):
    """
    Clase para mostrar pedidos desde la base de datos.
    """
    def __init__(self):
        super().__init__()

    def show(self):
        """
        Recupera y devuelve todos los pedidos desde la base de datos.

        Returns:
            list: Lista de pedidos, donde cada pedido es un diccionario con sus atributos.
        """
        query = "SELECT * FROM order_buy"
        self.cursor.execute(query)

        pedidos = self.cursor.fetchall()

        return pedidos

class Register(DatabaseConnection):
    """
    Clase para registrar un nuevo usuario en la base de datos.
    """

    def __init__(self, name, surname, email, phonenumber, address, password):
        super().__init__()
        self.bcrypt = Bcrypt()
        self.name = name
        self.surname = surname
        self.email = email
        self.phonenumber = phonenumber
        self.address = address
        self.password = password

    def check_user(self):
        """
        Verifica si ya existe un usuario con el mismo número de teléfono o correo electrónico.

        Returns:
            bool: True si ya existe un usuario con el mismo número de teléfono o correo electrónico, False en caso contrario.
        """
        query = "SELECT phonenumber, email FROM users WHERE phonenumber=%s OR email=%s"
        values = (self.phonenumber, self.email)
        self.cursor.execute(query, values)
        account = self.cursor.fetchone()
        return bool(account)

    def register(self):
        """
        Registra un nuevo usuario en la base de datos.

        Returns:
            bool: True si el registro fue exitoso, False en caso de error.
        """
        hashed_password = self.bcrypt.generate_password_hash(self.password).decode('utf-8')
        query = "INSERT INTO users (name, surname, email, phonenumber, address, password) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (self.name, self.surname, self.email, self.phonenumber, self.address, hashed_password)
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            return True
        except Exception as e:
            return False

    def close_connection(self):
        """Cierra la conexión a la base de datos."""
        self.cursor.close()
        self.conn.close()

        
class Login(DatabaseConnection):
    """
    Clase para gestionar el proceso de inicio de sesión de usuarios.
    """

    def __init__(self, username, password):
        super().__init__()
        self.bcrypt = Bcrypt()
        self.username = username
        self.password = password
        self.cart = []

    def check_credentials(self):
        """
        Verifica las credenciales del usuario y realiza el inicio de sesión.

        Returns:
            bool: True si las credenciales son válidas y el inicio de sesión es exitoso, False en caso contrario.
        """
        query = "SELECT * FROM users WHERE phonenumber = %s"
        values = (self.username,)
        self.cursor.execute(query, values)
        user = self.cursor.fetchone()

        if user and self.bcrypt.check_password_hash(user[6], self.password):
            session['loggedin'] = True  # Usamos True en lugar de 'True'
            session['id'] = user[0]
            session['username'] = self.username
            session['cart'] = self.cart
            session['login_attempts'] = 0
            return True

        return False  # Devolvemos False si las credenciales no son válidas

class GetUser(DatabaseConnection):
    def __init__(self):
        super().__init__()

    def get_username(self):
        query = "SELECT phonenumber FROM users WHERE id = %s"
        values = (session['id'],)

        self.cursor.execute(query,values)
        username = self.cursor.fetchone()

        return username
    
class Update(DatabaseConnection):
    """
    Clase para actualizar los datos de un usuario en la base de datos.
    """

    def __init__(self, name, surname, email, address, password):
        super().__init__()
        self.bcrypt = Bcrypt()
        self.name = name
        self.surname = surname
        self.email = email
        self.address = address
        self.password = password

    def update_user(self):
        """
        Actualiza los datos del usuario en la base de datos.

        Returns:
            bool|str: True si la actualización fue exitosa, o un mensaje de error si ocurrió un problema.
        """
        try:
            update_query = """
            UPDATE users
            SET name = %s, surname = %s, email = %s, address = %s
            WHERE id = %s
            """
            data = (self.name, self.surname, self.email, self.address, session['id'])

            if self.password:
                # Si se proporciona una nueva contraseña, genera y actualiza el hash
                hashed_password = self.bcrypt.generate_password_hash(self.password).decode('utf-8')
                update_query = """
                UPDATE users
                SET name = %s, surname = %s, email = %s, address = %s, password = %s
                WHERE id = %s
                """
                data = (self.name, self.surname, self.email, self.address, hashed_password, session['id'])

            self.cursor.execute(update_query, data)
            self.conn.commit()

            return True

        except Exception as e:
            return str(e)  # Retornar el mensaje de error

    def check_email_address(self):
        """
        Verifica si el nuevo correo electrónico ya pertenece a otro usuario.

        Returns:
            bool: True si el correo electrónico ya existe para otro usuario, False en caso contrario.
        """
        email_check_query = "SELECT id FROM users WHERE email = %s AND id != %s"
        email_data = (self.email, session['id'])
        self.cursor.execute(email_check_query, email_data)
        existing_user = self.cursor.fetchone()

        return bool(existing_user)  # Retornar True si el correo existe para otro usuario



class GetUserForUpdate(DatabaseConnection):
    """
    Clase para obtener los productos del usuario
    de la base de datos
    """
    def __init__(self):
        super().__init__()

    def user_values(self):
        """
        Obtiene los datos
    
        Returns:
            list: productos      
        """
        query = "SELECT * FROM users WHERE id = %s"
        values = (session['id'],)

        self.cursor.execute(query,values)
        username = self.cursor.fetchone()

        return username


class ForgotPassword(DatabaseConnection):
    """
    Clase para gestionar la recuperación de contraseña.
    """

    def __init__(self,email):
        super().__init__()
        
        self.email = email

    def check_email(self):
        """
        Verifica si el correo electrónico proporcionado existe en la base de datos.

        Returns:
            bool: True si el correo electrónico existe en la base de datos, False en caso contrario.
        """
        query = "SELECT email FROM users WHERE email = %s"
        values = (self.email,)
        self.cursor.execute(query, values)
        email = self.cursor.fetchone()

        return bool(email)  # Devuelve True si el correo electrónico existe en la base de datos

class UpdatePassword(DatabaseConnection):
    """
    Clase para gestionar la actualización de la contraseña de un usuario.
    """

    def __init__(self, password):
        super().__init__()
        self.bcrypt = Bcrypt()
        self.password = password

    def reset_password(self):
        """
        Actualiza la contraseña del usuario en la base de datos.

        Returns:
            bool: True si la actualización de contraseña fue exitosa, False en caso contrario.
        """
        try:
            # Verifica si el usuario con el correo electrónico existe en la base de datos
            query = "SELECT * FROM users WHERE email = %s"
            self.cursor.execute(query, (session['email_address'],))
            user = self.cursor.fetchone()

            if user:
                # Si el usuario existe, actualiza la contraseña
                hashed_password = self.bcrypt.generate_password_hash(self.password).decode('utf-8')

                update_query = "UPDATE users SET password = %s WHERE email = %s"
                self.cursor.execute(update_query, (hashed_password, session['email_address']))
                self.conn.commit()
                return True
            else:
                # Si el usuario no existe, no se actualiza la contraseña
                return False
        except mysql.connector.Error as err:
            return False
        finally:
            self.cursor.close()
            self.conn.close()


"""
Just for Admin User
"""
class Admin(DatabaseConnection):
    """
    Clase para gestionar las funciones de administrador.
    """

    def __init__(self, username, password):
        super().__init__()
        self.bcrypt = Bcrypt()
        self.username = username
        self.password = password

    def check_admin(self):
        """
        Verifica si las credenciales del administrador son válidas.

        Returns:
            bool: True si las credenciales son válidas y el administrador ha iniciado sesión, False en caso contrario.
        """
        query = "SELECT * FROM admin WHERE username = %s"
        values = (self.username,)

        self.cursor.execute(query, values)
        user = self.cursor.fetchone()

        if user and self.bcrypt.check_password_hash(user[2], self.password):
            session['loggedin'] = True  # Usamos True en lugar de 'True'
            session['is_admin'] = 1
            return True

        return False  # Devolvemos False si las credenciales no son válidas


class AddProduct(DatabaseConnection):
    """
    Clase para agregar nuevos productos a la base de datos.
    """

    def __init__(self, name, price, image):
        super().__init__()
        self.name = name
        self.price = price
        self.image = image

    def addproduct(self):
        """
        Agrega un nuevo producto a la base de datos.

        Returns:
            bool: True si la adición del producto fue exitosa, False en caso contrario.
        """
        try:
            # Genera un nombre único para la imagen
            new_image = time_stamp + self.image.filename

            # Guarda la imagen en la carpeta 'products'
            self.image.save('products/' + new_image)

            # Crea la consulta SQL para insertar el producto en la base de datos
            query = "INSERT INTO productos (nombre, precio, imagen) VALUES (%s, %s, %s)"
            values = (self.name, self.price, new_image)

            self.cursor.execute(query, values)
            self.conn.commit()

            return True
        except Exception as e:
            return False


class UpdateProduct(DatabaseConnection):
    """
    Clase para actualizar un producto en la base de datos.
    """

    def __init__(self, name, price, image, id):
        super().__init__()
        self.name = name
        self.price = price
        self.image = image
        self.id = id

    def updateproduct(self):
        """
        Actualiza un producto en la base de datos.

        Returns:
            bool: True si la actualización del producto fue exitosa, False en caso contrario.
        """
        try:
            if self.image.filename != '':
                # Genera un nuevo nombre único para la imagen
                new_updated_image = time_stamp + self.image.filename

                # Guarda la imagen actualizada en la carpeta 'products'
                self.image.save('products/' + new_updated_image)

                # Actualiza el campo 'imagen' en la base de datos
                self.cursor.execute("UPDATE productos SET imagen=%s WHERE id = %s", (new_updated_image, self.id))
                self.conn.commit()

            # Consulta SQL para actualizar el nombre y el precio
            query = "UPDATE productos SET nombre=%s, precio=%s WHERE id=%s"
            values = (self.name, self.price, self.id)

            self.cursor.execute(query, values)
            self.conn.commit()

            return True
        except Exception as e:
            return False


class GetProductsToUpdate(DatabaseConnection):
    """Esta clase se utiliza para obtener los detalles de un producto específico en la base de datos que se necesita actualizar. 
    
    Returns:
        Recibe como parámetro un ID de producto y recupera los datos
    """
    def __init__(self,id):
        super().__init__()

        self.id = id
    
    def get(self):
        self.cursor.execute('SELECT * FROM productos WHERE id = %s',(self.id,))
        products = self.cursor.fetchone()

        return products


class DeleteProduct(DatabaseConnection):
    """
    Clase para eliminar un producto de la base de datos.
    """

    def __init__(self, id):
        super().__init__()
        self.id = id

    def delete(self):
        """
        Elimina un producto de la base de datos.

        Returns:
            bool: True si la eliminación del producto fue exitosa, False en caso contrario.
        """
        try:
            query = "DELETE FROM productos WHERE id = %s"
            values = (self.id,)

            self.cursor.execute(query, values)
            self.conn.commit()

            return True
        except Exception as e:
            return False


class DeletePedido(DatabaseConnection):
    """
    Clase para eliminar un pedido de la base de datos.
    """

    def __init__(self, id):
        super().__init__()
        self.id = id

    def delete(self):
        """
        Elimina un pedido de la base de datos.

        Returns:
            bool: True si la eliminación del pedido fue exitosa, False en caso contrario.
        """
        try:
            query = "DELETE FROM order_buy WHERE id = %s"
            values = (self.id,)

            self.cursor.execute(query, values)
            self.conn.commit()

            return True
        except Exception as e:
            return False


class MarkOrder(DatabaseConnection):
    """
    Clase para marcar un pedido como enviado en la base de datos.
    """

    def __init__(self, id):
        super().__init__()
        self.id = id

    def mark(self):
        """
        Marca un pedido como enviado en la base de datos.

        Returns:
            bool: True si el marcado del pedido fue exitoso, False en caso contrario.
        """
        try:
            query = "UPDATE order_buy SET se_envia = 1 WHERE id = %s"
            values = (self.id,)

            self.cursor.execute(query, values)
            self.conn.commit()

            return True
        except Exception as e:
            return False
