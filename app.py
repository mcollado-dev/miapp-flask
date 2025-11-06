# Importamos Flask y la función render_template para renderizar las plantillas HTML
from flask import Flask, render_template

# Importamos la base de datos y el modelo Usuario desde el archivo models.py
from models import db, Usuario

# Librerías auxiliares
import secrets                # Para generar valores aleatorios (usado al asignar roles)
from collections import Counter  # Para contar elementos, en este caso roles de usuario
import io                     # Para manejar datos binarios en memoria
import base64                 # Para convertir imágenes a texto base64 (para incrustarlas en HTML)
import matplotlib.pyplot as plt  # Para generar gráficos de manera sencilla

# Creamos la aplicación Flask
app = Flask(__name__)

# ----------------------------
# CONFIGURACIÓN DE LA BASE DE DATOS
# ----------------------------
# Usamos MariaDB como base de datos real
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flaskuser:TU_CONTRASEÑA@192.168.56.105/miappdb'

# Desactivamos el seguimiento de modificaciones para mejorar el rendimiento
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializamos la base de datos con la configuración de Flask
db.init_app(app)

# ----------------------------
# CREACIÓN DE LA BASE DE DATOS Y DATOS DE PRUEBA
# ----------------------------
with app.app_context():
    db.create_all()  # Crea las tablas si no existen
    if Usuario.query.count() == 0:  # Si la tabla está vacía, añadimos datos de ejemplo
        nombres = [
            "Admin", "Juan", "María", "Carlos", "Ana", "Luis", "Sofía", "Miguel",
            "Lucía", "Pedro", "Carmen", "Jorge", "Elena", "Diego", "Laura",
            "Alberto", "Isabel", "Fernando", "Paula", "Ricardo"
        ]
        roles = [
            "Administrador", "Usuario", "Moderador", "Invitado",
            "SuperUsuario", "Editor", "Colaborador", "Visitante"
        ]
        # Recorremos los nombres y generamos un email y rol aleatorio para cada usuario
        for i, nombre in enumerate(nombres):
            email = f"{nombre.lower()}{i}@example.com"
            rol = secrets.choice(roles)
            usuario = Usuario(nombre=nombre, email=email, rol=rol)
            db.session.add(usuario)
        db.session.commit()  # Guardamos todos los usuarios en la base de datos


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
    # Obtenemos todos los usuarios de la base de datos
    usuarios = Usuario.query.all()
    total_usuarios = len(usuarios)

    # Contamos cuántos usuarios hay por rol
    roles_count = Counter([u.rol for u in usuarios])
    roles_labels = list(roles_count.keys())
    roles_data = list(roles_count.values())

    # Creamos un gráfico de barras horizontales con matplotlib
    plt.figure(figsize=(6, 4))
    plt.barh(roles_labels, roles_data, color='skyblue')
    plt.xlabel('Número de usuarios')
    plt.ylabel('Roles')
    plt.title('Distribución de roles')

    # Guardamos el gráfico en memoria (sin crear archivo físico)
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)

    # Convertimos el gráfico a base64 para poder mostrarlo directamente en el HTML
    grafico_base64 = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # Enviamos los datos y el gráfico al template HTML
    return render_template(
        'estadisticas.html',
        total_usuarios=total_usuarios,
        usuarios=usuarios,
        grafico_base64=grafico_base64
    )


# Ruta para la página de funciones
@app.route('/funciones')
def funciones():
    return render_template('funciones.html')


# Ruta para la página de documentación
@app.route('/documentacion')
def documentacion():
    return render_template('documentacion.html')


# Nueva ruta para la página de detalles
@app.route('/detalles')
def detalles():
    return render_template('detalles.html')


# ----------------------------
# EJECUCIÓN DE LA APLICACIÓN
# ----------------------------
if __name__ == '__main__':
    # Ejecutamos la aplicación Flask en el puerto 80, accesible desde cualquier IP
    app.run(host='0.0.0.0', port=80)


