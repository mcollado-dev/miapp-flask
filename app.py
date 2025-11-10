# ----------------------------
# app.py - Flask con CSRF, login y registro separados por GET y POST
# ----------------------------

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SelectField, EmailField
from wtforms.validators import DataRequired, Email
from collections import Counter
import io, base64
import matplotlib.pyplot as plt

# ----------------------------
# CREACIÓN DE LA APP
# ----------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_super_segura'

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flaskuser:PapayMama2016@192.168.56.105/miappdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Activar CSRF global
csrf = CSRFProtect(app)

# ----------------------------
# MODELO DE USUARIO
# ----------------------------
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    rol = db.Column(db.String(50), nullable=False)

# Crear tablas si no existen
with app.app_context():
    db.create_all()

# ----------------------------
# FORMULARIOS
# ----------------------------
class RegistroForm(FlaskForm):
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
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = EmailField('Correo electrónico', validators=[DataRequired(), Email()])

# ----------------------------
# RUTAS PÁGINAS PRINCIPALES
# ----------------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/funciones')
def funciones():
    return render_template('funciones.html')

@app.route('/documentacion')
def documentacion():
    return render_template('documentacion.html')

@app.route('/detalles')
def detalles():
    return render_template('detalles.html')

# ----------------------------
# ESTADÍSTICAS
# ----------------------------
@app.route('/estadisticas')
def estadisticas():
    usuarios = Usuario.query.all()
    total_usuarios = len(usuarios)
    roles_count = Counter([u.rol for u in usuarios])
    roles_labels = list(roles_count.keys())
    roles_data = list(roles_count.values())

    # Crear gráfico de barras horizontal
    plt.figure(figsize=(6,4))
    plt.barh(roles_labels, roles_data, color='skyblue')
    plt.xlabel('Número de usuarios')
    plt.ylabel('Roles')
    plt.title('Distribución de roles')

    # Convertir gráfico a base64 para mostrar en HTML
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    grafico_base64 = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return render_template('estadisticas.html',
                           total_usuarios=total_usuarios,
                           usuarios=usuarios,
                           grafico_base64=grafico_base64)

# ----------------------------
# REGISTRO DE USUARIOS
# ----------------------------
@app.route('/registro', methods=['GET'])
def registro_get():
    """Mostrar formulario de registro"""
    form = RegistroForm()
    return render_template('registro.html', form=form)

@app.route('/registro', methods=['POST'])
def registro_post():
    """Procesar formulario de registro"""
    form = RegistroForm()
    if form.validate_on_submit():
        nuevo_usuario = Usuario(
            nombre=form.nombre.data,
            email=form.email.data,
            rol=form.rol.data
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('estadisticas'))
    return render_template('registro.html', form=form)

# ----------------------------
# LOGIN DE USUARIOS
# ----------------------------
@app.route('/login', methods=['GET'])
def login_get():
    """Mostrar formulario de login"""
    form = LoginForm()
    return render_template('login.html', form=form)

@app.route('/login', methods=['POST'])
def login_post():
    """Procesar formulario de login"""
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(
            email=form.email.data,
            nombre=form.nombre.data
        ).first()
        if usuario:
            # Incluir rol en mensaje de bienvenida
            mensaje = f"Bienvenido, {usuario.nombre} ({usuario.rol})"
            return render_template('login.html', mensaje=mensaje, form=form)
        else:
            error = "Usuario no encontrado"
            return render_template('login.html', error=error, form=form)
    return render_template('login.html', form=form)

# ----------------------------
# EJECUCIÓN DE LA APP
# ----------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=80)


