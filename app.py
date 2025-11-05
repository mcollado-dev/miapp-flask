from flask import Flask, render_template
from models import db, Usuario
import secrets
from collections import Counter
import io
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///miapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    if Usuario.query.count() == 0:
        nombres = [
            "Admin", "Juan", "María", "Carlos", "Ana", "Luis", "Sofía", "Miguel",
            "Lucía", "Pedro", "Carmen", "Jorge", "Elena", "Diego", "Laura",
            "Alberto", "Isabel", "Fernando", "Paula", "Ricardo"
        ]
        roles = [
            "Administrador", "Usuario", "Moderador", "Invitado",
            "SuperUsuario", "Editor", "Colaborador", "Visitante"
        ]
        for i, nombre in enumerate(nombres):
            email = f"{nombre.lower()}{i}@example.com"
            rol = secrets.choice(roles)
            usuario = Usuario(nombre=nombre, email=email, rol=rol)
            db.session.add(usuario)
        db.session.commit()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/estadisticas')
def estadisticas():
    usuarios = Usuario.query.all()
    total_usuarios = len(usuarios)

    # Contar usuarios por rol
    roles_count = Counter([u.rol for u in usuarios])
    roles_labels = list(roles_count.keys())
    roles_data = list(roles_count.values())

    # Crear gráfico con matplotlib
    plt.figure(figsize=(6, 4))
    plt.barh(roles_labels, roles_data, color='skyblue')
    plt.xlabel('Número de usuarios')
    plt.ylabel('Roles')
    plt.title('Distribución de roles')

    # Guardar gráfico en memoria y convertirlo a base64
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    grafico_base64 = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return render_template(
        'estadisticas.html',
        total_usuarios=total_usuarios,
        usuarios=usuarios,
        grafico_base64=grafico_base64
    )


@app.route('/funciones')
def funciones():
    return render_template('funciones.html')


@app.route('/documentacion')
def documentacion():
    return render_template('documentacion.html')

@app.route('/detalles')
def detalles():
    return render_template('detalles.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

