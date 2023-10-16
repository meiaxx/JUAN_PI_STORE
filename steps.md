"JUAN PI PROJECT"

Guía de Configuración e Instalación
1. Configuración de la Base de Datos
(a) Establecer una nueva contraseña para el usuario root de la base de datos MySQL.

Para hacerlo, sigue estos pasos:

(1) Detén el servidor MySQL temporalmente para las configuraciones:


service mysqld stop
(2) Inicia MySQL con privilegios limitados para cambiar la contraseña. Esto deshabilitará el sistema de privilegios y permitirá el acceso a todas las bases de datos para todos los usuarios. Ejecuta el siguiente comando:


sudo mysqld_safe --skip-grant-tables --skip-networking &
(3) Ahora, cambia la contraseña del usuario root. Ejecuta los siguientes comandos:


mysql -u root

USE mysql;
UPDATE user SET password=PASSWORD('password') WHERE user='root';
Nota: Puedes mantener 'password' como la contraseña de la base de datos para que coincida con la configuración en config.py.

2. Crear la Base de Datos y Tablas para el Proyecto
**(a) Inicia MariaDB y ejecuta el archivo database.sql para crear la base de datos y tablas. Sigue estos pasos:

(1) Inicia MariaDB:


sudo service mysql start
(2) Ejecuta el script SQL:

mysql -u root -p < database.sql
Nota: Te pedirá la contraseña que estableciste anteriormente.

**(b) Confirma que la base de datos y las tablas se hayan creado correctamente:


mysql -u root -p
Luego, usa:


USE juan_pi;
SHOW TABLES;
3. Configuración de Bibliotecas
(a) Instala las bibliotecas necesarias ejecutando el siguiente comando:


pip3 install -r requirements.txt
Espera a que el proceso de instalación se complete.

4. Crear la Cuenta de Administrador
(a) Ejecuta el script para crear la cuenta de administrador:


python3 createsuperuser.py
Proporciona los datos del usuario administrador, incluyendo nombre, email, usuario y contraseña.

5. Iniciar el Servidor
(a) Por último, inicia el servidor ejecutando el siguiente comando:

python3 app.py

6. Acceder al Panel de Administración
**(a) Abre tu navegador web y navega a la ruta /admin de tu sistema, por ejemplo, http://127.0.0.1:5000/admin.

**(b) Inicia sesión en el panel de administración con las credenciales que configuraste previamente. Proporciona tu nombre de usuario y contraseña.

**(c) Una vez que hayas iniciado sesión, podrás acceder a la sección de productos. Busca la sección de productos en el panel de administración y selecciona "Agregar Producto" o una opción similar.

**(d) Completa los detalles del producto, como nombre, descripción, precio, etc., y guarda la información.

**(e) Repite el proceso para agregar más productos según sea necesario.
