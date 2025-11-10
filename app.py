# Importamos Flask y la función render_template para renderizar las plantillas HTML
from flask import Flask, render_template, request, redirect, url_for

# Importamos la base de datos y el modelo Usuario desde el archivo models.py
from models import db, Usuario

# Librerías auxiliares
from collections import Counter  # Para contar elementos, en este caso roles de usuario
import io                        # Para manejar datos binarios en memoria
import base64                    # Para convertir imágenes a texto base64 (para incrustarlas en HTML)
import matplotlib.pyplot as plt  # Para generar gráficos de manera sencilla

# Creamos la aplicación Flask
app = Flask(__name__)

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
# CREACIÓN DE LA BASE DE DATOS (sin generar usuarios automáticos)
# ----------------------------
with app.app_context():
    db.create_all()  # Crea las tablas si no existen


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
    usuarios = Usuario.query.all()
    total_usuarios = len(usuarios)
    roles_count = Counter([u.rol for u in usuarios])
    roles_labels = list(roles_count.keys())
    roles_data = list(roles_count.values())

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
# NUEVA RUTA: Registro de usuarios manualmente
# ----------------------------
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # Validación básica de seguridad para SonarQube
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        rol = request.form.get('rol', '').strip()

        if not nombre or not email or not rol:
            error = "Todos los campos son obligatorios."
            return render_template('registro.html', error=error)

        # Crear y guardar el nuevo usuario
        nuevo_usuario = Usuario(nombre=nombre, email=email, rol=rol)
        db.session.add(nuevo_usuario)
        db.session.commit()

        return redirect(url_for('estadisticas'))

    return render_template('registro.html')


# ----------------------------
# NUEVA RUTA: Login de usuarios registrados
# ----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Validación básica de seguridad para SonarQube
        email = request.form.get('email', '').strip()
        nombre = request.form.get('nombre', '').strip()

        if not email or not nombre:
            error = "Debes rellenar todos los campos."
            return render_template('login.html', error=error)

        # Buscar usuario en la base de datos
        usuario = Usuario.query.filter_by(email=email, nombre=nombre).first()

        if usuario:
            mensaje = f"Bienvenido, {usuario.nombre} ({usuario.rol})"
            return render_template('login.html', mensaje=mensaje)
        else:
            error = "Usuario no encontrado. Revisa tus datos o regístrate primero."
            return render_template('login.html', error=error)

    return render_template('login.html')


# ----------------------------
# EJECUCIÓN DE LA APLICACIÓN
# ----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

