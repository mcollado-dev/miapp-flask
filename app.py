# ----------------------------
# app.py - Flask con CSRF integrado usando Flask-WTF
# ----------------------------

# Importamos Flask y funciones necesarias
from flask import Flask, render_template, request, redirect, url_for
# SQLAlchemy para la base de datos
from flask_sqlalchemy import SQLAlchemy
# Flask-WTF y CSRFProtect para proteger formularios POST
from flask_wtf import FlaskForm, CSRFProtect
# Campos de formulario y validadores
from wtforms import StringField, SelectField, EmailField
from wtforms.validators import DataRequired, Email
# Librerías auxiliares para estadísticas
from collections import Counter
import io
import base64
import matplotlib.pyplot as plt

# ----------------------------
# CREACIÓN DE LA APP FLASK
# ----------------------------
app = Flask(__name__)

# Clave secreta para sesiones y CSRF
# Siempre debe ser secreta en producción
app.config['SECRET_KEY'] = 'tu_clave_secreta_super_segura'

# ----------------------------
# CONFIGURACIÓN DE LA BASE DE DATOS
# ----------------------------
# Conexión a MariaDB real
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flaskuser:PapayMama2016@192.168.56.105/miappdb'
# Desactivamos seguimiento de cambios para mejorar rendimiento
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializamos SQLAlchemy
db = SQLAlchemy(app)

# ----------------------------
# ACTIVAR CSRF GLOBAL
# ----------------------------
# Protege automáticamente todas las rutas POST
csrf = CSRFProtect(app)

# ----------------------------
# MODELO DE USUARIO
# ----------------------------
class Usuario(db.Model):
    """
    Modelo de usuario:
    - id: clave primaria
    - nombre: nombre del usuario
    - email: correo electrónico único
    - rol: rol del usuario
    """
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    rol = db.Column(db.String(50), nullable=False)

# ----------------------------
# CREACIÓN DE TABLAS SI NO EXISTEN
# ----------------------------
with app.app_context():
    db.create_all()

# ----------------------------
# FORMULARIOS CON WTForms
# ----------------------------
class RegistroForm(FlaskForm):
    """Formulario de registro de usuarios"""
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = EmailField('Correo electrónico', validators=[DataRequired(), Email()])
    rol = SelectField('Rol', choices=[
        ('Usuario', 'Usuario'),
        ('Administrador', 'Administrador'),
        ('Moderador', 'Moderador'),
        ('Invitado', 'Invitado'),
        ('Editor', 'Editor'),
        ('Colaborador', 'Colaborador'),
        ('Visitante', 'Visitante')
    ], validators=[DataRequired()])

class LoginForm(FlaskForm):
    """Formulario de login de usuarios"""
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = EmailField('Correo electrónico', validators=[DataRequired(), Email()])

# ----------------------------
# RUTAS PRINCIPALES
# ----------------------------
@app.route('/')
def home():
    """Página principal de la aplicación"""
    return render_template('index.html')

@app.route('/funciones')
def funciones():
    """Página de funciones"""
    return render_template('funciones.html')

@app.route('/documentacion')
def documentacion():
    """Página de documentación"""
    return render_template('documentacion.html')

@app.route('/detalles')
def detalles():
    """Página de detalles"""
    return render_template('detalles.html')

# ----------------------------
# ESTADÍSTICAS DE USUARIOS
# ----------------------------
@app.route('/estadisticas')
def estadisticas():
    """
    Página que muestra estadísticas de usuarios:
    - Total de usuarios
    - Distribución de roles
    - Gráfico en base64
    """
    usuarios = Usuario.query.all()
    total_usuarios = len(usuarios)

    # Contar roles de usuarios
    roles_count = Counter([u.rol for u in usuarios])
    roles_labels = list(roles_count.keys())
    roles_data = list(roles_count.values())

    # Crear gráfico de barras horizontal
    plt.figure(figsize=(6,4))
    plt.barh(roles_labels, roles_data, color='skyblue')
    plt.xlabel('Número de usuarios')
    plt.ylabel('Roles')
    plt.title('Distribución de roles')

    # Convertir gráfico a base64 para incrustar en HTML
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    grafico_base64 = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # Renderizar plantilla con estadísticas
    return render_template('estadisticas.html',
                           total_usuarios=total_usuarios,
                           usuarios=usuarios,
                           grafico_base64=grafico_base64)

# ----------------------------
# REGISTRO DE USUARIOS
# ----------------------------
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """
    Ruta de registro de usuarios:
    - GET: muestra el formulario
    - POST: valida y guarda usuario
    - CSRF automáticamente protegido por Flask-WTF
    """
    form = RegistroForm()
    if form.validate_on_submit():
        # Guardar nuevo usuario en la base de datos
        nuevo_usuario = Usuario(
            nombre=form.nombre.data,
            email=form.email.data,
            rol=form.rol.data
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        # Redirigir a estadísticas después de guardar
        return redirect(url_for('estadisticas'))

    # Renderizar plantilla con el formulario
    return render_template('registro.html', form=form)

# ----------------------------
# LOGIN DE USUARIOS
# ----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Ruta de login de usuarios:
    - GET: muestra el formulario
    - POST: valida usuario y muestra mensaje
    - CSRF protegido automáticamente
    """
    form = LoginForm()
    if form.validate_on_submit():
        # Buscar usuario en la base de datos
        usuario = Usuario.query.filter_by(email=form.email.data, nombre=form.nombre.data).first()
        if usuario:
            # Usuario encontrado, mostrar mensaje de bienvenida
            mensaje = f"Bienvenido, {usuario.nombre} ({usuario.rol})"
            return render_template('login.html', mensaje=mensaje, form=form)
        else:
            # Usuario no encontrado
            error = "Usuario no encontrado. Revisa tus datos o regístrate primero."
            return render_template('login.html', error=error, form=form)

    # Renderizar formulario de login
    return render_template('login.html', form=form)

# ----------------------------
# EJECUCIÓN DE LA APP
# ----------------------------
if __name__ == '__main__':
    # Ejecutar la app en host 0.0.0.0 puerto 80
    app.run(host='0.0.0.0', port=80)

