from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SelectField, EmailField
from wtforms.validators import DataRequired, Email
from collections import Counter
import io, base64
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_super_segura'

# Conexión a MariaDB real
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flaskuser:PapayMama2016@192.168.56.105/miappdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
csrf = CSRFProtect(app)  # CSRF activado globalmente

# ----------------------------
# MODELO DE USUARIO
# ----------------------------
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    rol = db.Column(db.String(50), nullable=False)

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
# RUTAS
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

@app.route('/estadisticas')
def estadisticas():
    usuarios = Usuario.query.all()
    total_usuarios = len(usuarios)
    roles_count = Counter([u.rol for u in usuarios])
    roles_labels = list(roles_count.keys())
    roles_data = list(roles_count.values())

    plt.figure(figsize=(6,4))
    plt.barh(roles_labels, roles_data, color='skyblue')
    plt.xlabel('Número de usuarios')
    plt.ylabel('Roles')
    plt.title('Distribución de roles')

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

@app.route('/registro', methods=['GET', 'POST'])
def registro():
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data, nombre=form.nombre.data).first()
        if usuario:
            # Mostrar el rol en el mensaje de bienvenida
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

