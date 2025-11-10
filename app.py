# ----------------------------
# APP.PY - Aplicación Flask con registro, login, estadísticas y CSRF
# ----------------------------

# Importamos Flask y funciones necesarias
from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Usuario  # Base de datos y modelo Usuario
from collections import Counter  # Para contar roles
import io                        # Para manejar imágenes en memoria
import base64                    # Para convertir imágenes a base64
import matplotlib.pyplot as plt  # Para gráficos
import secrets                    # Para generar tokens CSRF

# ----------------------------
# CREACIÓN DE LA APLICACIÓN FLASK
# ----------------------------
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Clave secreta para sesiones y CSRF

# ----------------------------
# CONFIGURACIÓN DE LA BASE DE DATOS
# ----------------------------
# Conexión a MariaDB real
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flaskuser:PapayMama2016@192.168.56.105/miappdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializamos la base de datos
db.init_app(app)

# Creamos tablas si no existen
with app.app_context():
    db.create_all()

# ----------------------------
# RUTAS PRINCIPALES
# ----------------------------

@app.route('/')
def home():
    """Página principal"""
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
# Ruta de estadísticas
# ----------------------------
@app.route('/estadisticas')
def estadisticas():
    usuarios = Usuario.query.all()
    total_usuarios = len(usuarios)
    roles_count = Counter([u.rol for u in usuarios])
    roles_labels = list(roles_count.keys())
    roles_data = list(roles_count.values())

    # Generamos gráfico
    plt.figure(figsize=(6, 4))
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

# ----------------------------
# RUTA DE REGISTRO CON CSRF
# ----------------------------
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # Validación CSRF
        token_form = request.form.get('csrf_token')
        token_sesion = session.pop('csrf_token', None)
        if not token_form or token_form != token_sesion:
            error = "Solicitud inválida."
            csrf_token = secrets.token_hex(16)
            session['csrf_token'] = csrf_token
            return render_template('registro.html', error=error, csrf_token=csrf_token)

        # Validación de campos
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        rol = request.form.get('rol', '').strip()
        if not nombre or not email or not rol:
            error = "Todos los campos son obligatorios."
            csrf_token = secrets.token_hex(16)
            session['csrf_token'] = csrf_token
            return render_template('registro.html', error=error, csrf_token=csrf_token)

        # Crear usuario
        nuevo_usuario = Usuario(nombre=nombre, email=email, rol=rol)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('estadisticas'))

    # GET: generamos token CSRF
    csrf_token = secrets.token_hex(16)
    session['csrf_token'] = csrf_token
    return render_template('registro.html', csrf_token=csrf_token)

# ----------------------------
# RUTA DE LOGIN CON CSRF
# ----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Validación CSRF
        token_form = request.form.get('csrf_token')
        token_sesion = session.pop('csrf_token', None)
        if not token_form or token_form != token_sesion:
            error = "Solicitud inválida."
            csrf_token = secrets.token_hex(16)
            session['csrf_token'] = csrf_token
            return render_template('login.html', error=error, csrf_token=csrf_token)

        # Validación de campos
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        if not nombre or not email:
            error = "Debes rellenar todos los campos."
            csrf_token = secrets.token_hex(16)
            session['csrf_token'] = csrf_token
            return render_template('login.html', error=error, csrf_token=csrf_token)

        # Buscar usuario
        usuario = Usuario.query.filter_by(nombre=nombre, email=email).first()
        if usuario:
            mensaje = f"Bienvenido, {usuario.nombre} ({usuario.rol})"
            csrf_token = secrets.token_hex(16)
            session['csrf_token'] = csrf_token
            return render_template('login.html', mensaje=mensaje, csrf_token=csrf_token)
        else:
            error = "Usuario no encontrado. Revisa tus datos o regístrate primero."
            csrf_token = secrets.token_hex(16)
            session['csrf_token'] = csrf_token
            return render_template('login.html', error=error, csrf_token=csrf_token)

    # GET: generamos token CSRF
    csrf_token = secrets.token_hex(16)
    session['csrf_token'] = csrf_token
    return render_template('login.html', csrf_token=csrf_token)

# ----------------------------
# EJECUCIÓN DE LA APLICACIÓN
# ----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

