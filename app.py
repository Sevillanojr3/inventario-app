from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from config import Config
import re
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:2412@localhost/InventarioApp'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Rol(db.Model):
    __tablename__ = 'Roles'
    id = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50), nullable=False)

class Local(db.Model):
    __tablename__ = 'Locales'
    id_local = db.Column(db.Integer, primary_key=True)
    nombre_local = db.Column(db.String(100), nullable=False)

class Usuario(db.Model):
    __tablename__ = 'Usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    contrasena = db.Column(db.String(100), nullable=False)
    nombre_usuario = db.Column(db.String(100), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('Roles.id'))
    id_local = db.Column(db.Integer, db.ForeignKey('Locales.id_local'))

class Producto(db.Model):
    __tablename__ = 'Productos'
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre_producto = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    id_local = db.Column(db.Integer, db.ForeignKey('Locales.id_local'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            flash('Por favor, inicia sesión para acceder a esta página', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Ruta principal
@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('index.html', loggedin=session.get('loggedin'), id_rol=session.get('id_rol'))

# Ruta para pedidos
@app.route('/pedidos', methods=['GET', 'POST'])
@login_required
def pedidos():
    if request.method == 'POST':
        # Lógica para manejar el pedido
        producto_id = request.form['producto_id']
        cantidad = int(request.form['cantidad'])
        local_id = session.get('id_local')

        producto = Producto.query.filter_by(id_producto=producto_id, id_local=local_id).first()
        if producto and producto.cantidad >= cantidad:
            producto.cantidad -= cantidad
            db.session.commit()
            flash('Pedido realizado con éxito', 'success')
        else:
            flash('No hay suficiente stock para realizar el pedido', 'error')
        return redirect(url_for('pedidos'))

    # Recuperar productos disponibles para el local del usuario
    productos = Producto.query.filter(Producto.cantidad > 0, Producto.id_local == session.get('id_local')).all()
    return render_template('pedidos.html', productos=productos, loggedin=session.get('loggedin'), id_rol=session.get('id_rol'))

# Ruta de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password == confirm_password:
            # Guardar la contraseña tal cual (sin encriptar) temporalmente
            nuevo_usuario = Usuario(
                nombre=nombre,
                apellido=apellido,
                contrasena=password,  # No encriptada
                id_rol=2,  # O el rol que corresponda
                id_local=1  # O el local que corresponda
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            flash('Registro exitoso, ahora puedes iniciar sesión', 'success')
            return redirect(url_for('login'))
        else:
            flash('Las contraseñas no coinciden, por favor inténtalo de nuevo', 'danger')

    return render_template('register.html', loggedin=session.get('loggedin'), id_rol=session.get('id_rol'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        print(f"Datos recibidos: {data}")  # Esto imprimirá los datos recibidos
        username = data.get('username')
        password = data.get('password')
        print(f"Username: {username}, Password: {password}")  # Para verificar si llegan bien

        user = Usuario.query.filter_by(nombre_usuario=username).first()

        if user and user.contrasena == password:  # Temporarily using plain text comparison
            session['loggedin'] = True
            session['id_usuario'] = user.id_usuario
            session['nombre_usuario'] = user.nombre_usuario
            session['id_rol'] = user.id_rol
            session['id_local'] = user.id_local
            return jsonify({'success': True, 'redirect': url_for('index')})
        else:
            return jsonify({'success': False, 'message': 'Usuario o contraseña incorrectos'}), 401
    return render_template('login.html', loggedin=session.get('loggedin'), id_rol=session.get('id_rol'))

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'success')
    return redirect(url_for('login'))

# Ruta para el inventario del administrador
@app.route('/admin/inventario')
@login_required
def admin_inventario():
    if session.get('id_rol') != 1:
        flash('No tienes permiso para acceder a esta página', 'danger')
        return redirect(url_for('index'))
    
    productos = Producto.query.all()
    return render_template('admin_inventario.html', productos=productos, loggedin=session.get('loggedin'), id_rol=session.get('id_rol'))

if __name__ == '__main__':
    app.run(debug=True)
