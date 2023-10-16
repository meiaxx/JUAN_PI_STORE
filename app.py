from database import (
    Register, Login, GetUser, Update, GetUserForUpdate, ForgotPassword, UpdatePassword,
    ShowProducts, ShowPedidos, Admin, DeleteProduct, DeletePedido, AddProduct, MarkOrder,
    GetProductsToUpdate, UpdateProduct
)
from config import *
import mysql.connector
import json

@app.errorhandler(404)
def not_found_error(error):
    # Realizar una redirección a la página de inicio después de mostrar el error 404
    return redirect(url_for('home'))

CARPETA = os.path.join("products")
app.config["CARPETA"] = CARPETA

@app.route('/uploads/<picture>')
def uploads(picture):
    return send_from_directory(app.config['CARPETA'],picture)

@app.route('/')
def home():
    """ Main Page """
    products = ShowProducts().show()
    return render_template('index.html',products=products)

@app.route('/about')
def about():
    """ About us Page"""
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        mensaje = request.form.get('mensaje')

        if not nombre or not correo or not mensaje:
            flash('Por favor, completa todos los campos', 'danger')
        else:
            msg = Message('Nuevo mensaje de contacto',
                          sender=correo,
                          recipients=['clashnelissa@gmail.com'])  # Reemplaza con la dirección de correo de los administradores

            msg.body = f'Nombre: {nombre}\nCorreo: {correo}\nMensaje: {mensaje}'

            try:
                mail.send(msg)
                flash('Mensaje enviado con éxito', 'success')
            except Exception as e:
                flash('Error al enviar el mensaje', 'danger')

    return render_template('contact.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registro de usuario.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        phonenumber = request.form.get('phonenumber')
        address = request.form.get('address')
        password = request.form.get('password')
        password_confirmed = request.form.get('confirm-password')

        if not name or not surname or not email or not phonenumber or not address or not password:
            flash('Por favor, completa todos los campos', 'danger')
        elif password != password_confirmed:
            flash('Las contraseñas no coinciden', 'danger')
        else:
            register_db = Register(name, surname, email, phonenumber, address, password)

            if register_db.check_user():
                flash('La cuenta ya existe', 'danger')
            else:
                if register_db.register():
                    flash('Cuenta creada con éxito', 'success')
                    # Puedes redirigir al usuario a otra página después del registro si es necesario
                else:
                    flash('Error al crear la cuenta', 'danger')

            register_db.close_connection()

    return render_template('register.html')


@app.route('/login',methods=['GET','POST'])
def login():
    """ User Login """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Login class instance
        login = Login(username,password)

        # check username/password 
        if login.check_credentials():
            return redirect(url_for('account'))
        else:
            flash('Usuario (o) Contraseña Incorrecta','error')

            # increment  fails..
            session['login_attempts'] = session.get('login_attempts', 0) + 1

            if session.get('login_attempts', 0) >= 3:
                # Llama a la función JavaScript para mostrar el modal
                return render_template('login.html', show_reset_password_modal=True)

    return render_template('login.html')

@app.route('/forgot_password',methods=['GET','POST'])
def forgot_password():
    if request.method == 'POST':
        # get email
        email = request.form['email']

        forgotpass = ForgotPassword(email)

        if forgotpass.check_email():
            reset_link = generate_reset_link(email)
            reset_url = f"http://192.168.1.106:3000/reset_password/{reset_link}"

            if EmailSender.send_reset_password(email,reset_url):
                 flash('Se ha enviado un correo electrónico de restablecimiento de contraseña.', 'success')
                 session['email_address'] = email
            else:
                flash('Hubo un problema al enviar el correo electrónico. Inténtalo de nuevo.', 'danger')
        else:
            flash("Está cuenta de Correo Electronico, No existe","error")

    return render_template('forgot.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Valida el token
    email = validate_reset_token(token)

    if not email:
        flash('El enlace de restablecimiento de contraseña es inválido o ha caducado.', 'danger')
        return redirect(url_for('login'))  # login

    if request.method == 'POST' and 'email_address' in session:
        # Actualiza la contraseña del usuario en la base de datos
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if password != confirm_password:
            flash('Las contraseñas con coincided','red')

        # update password here..
        update_password = UpdatePassword(password)

        if update_password.reset_password():
            flash('Contraseña restablecida con éxito. Ahora puedes iniciar sesión con tu nueva contraseña.', 'success')
            return redirect(url_for('login'))  # Redirige a la página de inicio de sesión
        else:
            flash("Error, al actualizar contraseña!","red")


    return render_template('reset_password.html', token=token)  # Muestra el formulario de restablecimiento de contraseña


# route auth check
@app.before_request
def require_login():
    if request.endpoint == 'account' and 'loggedin' not in session:
        return redirect(url_for('login'))

@app.route('/account')
def account():
    """ Username Account """
    user = GetUser()
    user_name  = user.get_username()
    username = re.sub(r'[\'\(\),]', '', str(user_name))

    # get products
    products = ShowProducts().show()
    
    return render_template('account.html',user=username,products=products)


@app.before_request
def require_login():
    if request.endpoint == 'profile' and 'loggedin' not in session:
        return redirect(url_for('login'))

@app.route('/profile',methods=['GET','POST'])
def profile():
    user = GetUserForUpdate().user_values()

    if request.method == 'POST':
        # get data
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        address = request.form['address']
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        # check passwords
        if password != confirm_password:
            flash("Las, Contraseñas no Coinciden","error")

        update = Update(name,surname,email,address,password)

        if update.check_email_address():
            flash("La, Cuenta de Email ya está siendo usada",'error')
        else:
            update.update_user()
            user = GetUserForUpdate().user_values()
            flash("datos actualizdos exitosamente!",'success')
    
    return render_template('profile.html',user=user)

@app.route('/logout')
def logout():
    """ log out of the user """
    session.pop('loggedin',None)
    flash('Has cerrado Sesión','success')
    return redirect(url_for('login'))

@app.route('/comprar', methods=['POST'])
def comprar():
    if request.method == 'POST':
        try:
            # Obtén los datos de productos del formulario
            products_json = request.form['products']
            products_to_buy = json.loads(products_json)

            # Verificar si el carrito está vacío
            if len(products_to_buy) == 0:
                flash('Tu carrito está vacío. Agrega productos antes de finalizar la compra.', 'error')
            else:
                # Conecta a la base de datos
                conn = mysql.connector.connect(
                    host=DB_HOST,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME
                )

                cursor = conn.cursor()

                # Itera a través de los productos y realiza la inserción o actualización en la base de datos
                for product in products_to_buy:
                    nombre_producto = product['title']
                    cantidad = product['amount']
                    precio = float(product['price'])
                    
                    # Obtén el producto_id correspondiente basado en el nombre del producto
                    cursor.execute("SELECT id FROM productos WHERE nombre = %s", (nombre_producto,))
                    producto_id = cursor.fetchone()[0]

                    # Verificar si el producto ya está en el carrito del usuario
                    cursor.execute("SELECT * FROM detalle_compra WHERE usuario_id = %s AND producto_id = %s", (session['id'], producto_id))
                    existing_item = cursor.fetchone()

                    if existing_item:
                        # Si existe, actualiza la cantidad
                        new_cantidad = existing_item[3] + cantidad
                        cursor.execute("UPDATE detalle_compra SET cantidad = %s WHERE usuario_id = %s AND producto_id = %s", (new_cantidad, session['id'], producto_id))
                    else:
                        # Si no existe, inserta un nuevo registro
                        cursor.execute("INSERT INTO detalle_compra (usuario_id, producto_id, nombre_producto, cantidad, precio) VALUES (%s, %s, %s, %s, %s)",
                                        (session['id'], producto_id, nombre_producto, cantidad, precio))
                    
                conn.commit()

                # Cierra la conexión a la base de datos
                conn.close()

                # Redirige a la página de checkout solo si se han agregado productos
                return redirect(url_for('checkout'))

        except Exception as e:
            # Manejar errores, por ejemplo, si los datos enviados no son válidos.
            pass

    # Esto renderizará la página de compra, donde el usuario puede ver su carrito y hacer clic en "Finalizar Compra".
    return render_template('account.html')


@app.before_request
def require_login():
    if request.endpoint == 'checkout' and 'loggedin' not in session:
        return redirect(url_for('login'))

@app.route('/checkout', methods=['GET','POST'])
def checkout():
    if request.method == 'POST':
        # Obtener los datos del formulario
        full_name = request.form['full_name']
        email_address = request.form['email_address']
        postal_code = request.form['postal_code']
        muni = request.form['muni']
        phone = request.form['phone']
        urbanization = request.form['urbanization']
        totalCard = request.form['totalCard']  # Aquí se obtiene el totalCard del input oculto


        # Realizar la inserción en la base de datos
        try:
            conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )

            cursor = conn.cursor()

            # Insertar datos en la tabla Order
            cursor.execute("INSERT INTO `order_buy` (nombre, correo, ubicacion, codigo_postal, numero_telefono, cantidad_total) VALUES (%s, %s, %s, %s, %s, %s)",
                            (full_name, email_address, muni, postal_code, phone, totalCard))
            
            conn.commit()

            # Cerrar la conexión a la base de datos
            conn.close()

            # Redirigir o mostrar un mensaje de éxito
            flash("Pedido, Exitoso Gracias...",'success')  # Puedes redirigir a una página de éxito de compra

        except Exception as e:
            # Manejar errores, por ejemplo, mostrar un mensaje de error
            pass

    return render_template('checkout.html')

# Función para verificar si un usuario está autenticado y es administrador
def is_admin():
    return session.get('loggedin') and session.get('is_admin') == 1

# Decorador personalizado para proteger rutas de administrador
def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            flash('No tienes permiso para acceder a esa página', 'error')
            return redirect(url_for('admin'))  # O redirige a otra página
        return func(*args, **kwargs)
    return decorated_function

@app.route('/admin',methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        AdminLogin = Admin(username,password)

        if AdminLogin.check_admin():
            return redirect(url_for('panel'))
        else:
            flash("(usuario/contraseña) son incorrectos!","error")

    return render_template("admin/auth.html")


# Aplica el decorador a las rutas que requieren autorización de administrador
@app.route('/panel')
@admin_required
def panel():
    # Tu código para la vista del panel de administración aquí
    return render_template('admin/panel.html')

@app.route('/list_products')
@admin_required
def list_products():
    products = ShowProducts().show()

    return render_template('admin/list-products.html',products=products)

@app.route('/list_pedidos')
@admin_required
def list_pedidos():
    pedidos = ShowPedidos().show()

    return render_template('admin/list_pedidos.html',pedidos=pedidos)


# CRUD IN ADMIN
@app.route('/add_product',methods=['GET','POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form['product_name']
        price = request.form['price']
        image = request.files['imagen']

        # check
        if image and allowed_file(image.filename):
            addProduct = AddProduct(name,price,image)
            addProduct.addproduct()

            return redirect(url_for('list_products'))

    return render_template('admin/add_product.html')


# Update
@app.route('/edit_product/<int:id>')
@admin_required
def edit_product(id):
    ptu =  GetProductsToUpdate(id).get()
    return render_template('admin/update_product.html',products=ptu)

@app.route('/update_product',methods=['POST'])
@admin_required
def update_product():
    name = request.form['product_name']
    price = request.form['price']
    image = request.files['imagen']
    id = request.form['id']

    if not allowed_file(image.filename):
        flash('Tipo de archivo no válido. Los tipos de archivo válidos son: png, jpg, jpeg, gif')

    updateProducts = UpdateProduct(name,price,image,id)
    updateProducts.updateproduct()
        
    return redirect(url_for('list_products'))
    

@app.route('/delete_product/<int:id>')
@admin_required
def delete_product(id):
    deleteProduct = DeleteProduct(id)

    deleteProduct.delete()

    return redirect(url_for('list_products'))


@app.route('/delete_order/<int:id>')
@admin_required
def delete_order(id):
    delete_pedido = DeletePedido(id)

    delete_pedido.delete()

    return redirect(url_for('list_pedidos'))

# marca el envio
@app.route('/mark_order/<int:id>')
@admin_required
def mark_order(id):
    order_marked = MarkOrder(id).mark()

    return redirect(url_for('list_pedidos'))

@app.route('/admin_logout')
def admin_logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('admin'))  # Redirige a la página de inicio de sesión

if __name__ == "__main__":
    app.run(debug=False)
