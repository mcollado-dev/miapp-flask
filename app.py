# ----------------------------
# APP.PY - Aplicación Flask con registro, login y CSRF
# ----------------------------

# Importamos Flask y funciones necesarias para renderizar templates y manejar solicitudes
from flask import Flask, render_template, request, redirect, url_for, session

# Importamos la base de datos y el modelo Usuario desde el archivo models.py
from models import db, Usuario

# Librerías auxiliares
from collections import Counter  # Para contar elementos, en este caso roles de usuario
import io                        # Para manejar datos binarios en memoria
import base64                    # Para convertir imágenes a texto base64 (para incrustarlas en HTML)
import matplotlib.pyplot as plt  # Para generar gráficos de manera sencilla
import secrets                    # Para generar tokens CSRF y proteger formularios

# ----------------------------
# CREACIÓN DE LA APLICACIÓN FLASK
# ----------------------------
app = Flask(__name__)

# Clave secreta necesaria para sesiones y tokens CSRF
app.secret_key = secrets.token_hex(16)

# ----------------------------
# CONFIGURACIÓN DE LA BASE DE DATOS
# ----------------------------
# Usamos MariaDB como base de datos real
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flaskuser:PapayMama2016@192.168.56.105/miappdb'

# Desactivamos el seguimiento de modificaciones para mejorar el rendimiento
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializamos la base de datos con la configuración de Flask
db.init_app(app)

# ----------------------------
# CREACIÓN DE LA BASE DE DATOS (si no existen tablas)
# ----------------------------
with app.app_context():
    db.create_all()  # Crea las tablas según el modelo Usuario

# ----------------------------
# RUTAS PRINCIPALES DE LA APLICACIÓN
# ----------------------------

# Ruta principal: renderiza la página de inicio
@app.route('/')
def home():
    return render_template('index.html')

# Ruta para mostrar estadísticas con gráfico
@app.route('/estadisticas')
def estadisticas():
    # Obtenemos todos los usuarios
    usuarios = Usuario.query.all()
    total_usuarios = len(usuarios)

    # Contamos los roles para el gráfico
    roles_count = Counter([u.rol for u in usuarios])
    roles_labels = list(roles_count.keys())
    roles_data = list(roles_count.values())

    # Generamos gráfico de barras horizontal
    plt.figure(figsize=(6, 4))
    plt.barh(roles_labels, roles_data, color='skyblue')
    plt.xlabel('Número de usuarios')
    plt.ylabel('Roles')
    plt.title('Distribución de roles')

    # Convertimos el gráfico a base64 para incrustarlo en HTML
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    grafico_base64 = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # Renderizamos la plantilla con los datos
    return render_template('estadisticas.html',
                           total_usuarios=total_usuarios,
                           usuarios=usuarios,
                           grafico_base64=grafico_base64)

# Ruta para mostrar la página de funciones
@app.route('/funciones')
def funciones():
    return render_template('funciones.html')

# Ruta para mostrar documentación
@app.route('/documentacion')
def documentacion():
    return render_template('documentacion.html')

# Ruta para mostrar detalles
@app.route('/detalles')
def detalles():
    return render_template('detalles.html')

# ----------------------------
# NUEVA RUTA: Registro de usuarios manualmente con CSRF
# ----------------------------
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # Validación del token CSRF para evitar solicitudes maliciosas
        token_form = request.form.get('csrf_token')
        token_sesion = session.pop('csrf_token', None)
        if not token_form or token_form != token_sesion:
            error = "Solicitud inválida."
            return render_template('registro.html', error=error)

        # Obtenemos los datos del formulario
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        rol = request.form.get('rol', '').strip()

        # Validación de campos obligatorios
        if not nombre or not email or not rol:
            error = "Todos los campos son obligatorios."
            return render_template('registro.html', error=error)

        # Creamos y guardamos el nuevo usuario en la base de datos
        nuevo_usuario = Usuario(nombre=nombre, email=email, rol=rol)
        db.session.add(nuevo_usuario)
        db.session.commit()

        # Redirigimos a la página de estadísticas
        return redirect(url_for('estadisticas'))

    # Para GET: generamos token CSRF y lo enviamos al formulario
    csrf_token = secrets.token_hex(16)
    session['csrf_token'] = csrf_token
    return render_template('registro.html', csrf_token=csrf_token)

# ----------------------------
# NUEVA RUTA: Login de usuarios registrados con CSRF
# ----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Validación del token CSRF
        token_form = request.form.get('csrf_token')
        token_sesion = session.pop('csrf_token', None)
        if not token_form or token_form != token_sesion:
            error = "Solicitud inválida."
            return render_template('login.html', error=error)

        # Obtenemos los datos del formulario
        email = request.form.get('email', '').strip()
        nombre = request.form.get('nombre', '').strip()

        # Validación de campos obligatorios
        if not email or not nombre:
            error = "Debes rellenar todos los campos."
            return render_template('login.html', error=error)

        # Buscamos al usuario en la base de datos
        usuario = Usuario.query.filter_by(email=email, nombre=nombre).first()

        if usuario:
            # Si existe, mostramos mensaje de bienvenida
            mensaje = f"Bienvenido, {usuario.nombre} ({usuario.rol})"
            return render_template('login.html', mensaje=mensaje)
        else:
            # Si no existe, mostramos error
            error = "Usuario no encontrado. Revisa tus datos o regístrate primero."
            return render_template('login.html', error=error)

    # Para GET: generamos token CSRF y lo enviamos al formulario
    csrf_token = secrets.token_hex(16)
    session['csrf_token'] = csrf_token
    return render_template('login.html', csrf_token=csrf_token)

# ----------------------------
# EJECUCIÓN DE LA APLICACIÓN
# ----------------------------
if __name__ == '__main__':
    # Ejecuta la app en el host 0.0.0.0 y puerto 80
    app.run(host='0.0.0.0', port=80)


