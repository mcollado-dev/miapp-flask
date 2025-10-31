from flask import Flask, render_template
from models import db, Usuario

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///miapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Inicializar la base de datos al arrancar la app
with app.app_context():
    db.create_all()
    if Usuario.query.count() == 0:
        # Añadir usuarios de ejemplo
        usuarios = [
            Usuario(nombre='Manuel Collado', email='manuel@example.com', rol='Administrador'),
            Usuario(nombre='Laura Pérez', email='laura@example.com', rol='Editor'),
            Usuario(nombre='Carlos Gómez', email='carlos@example.com', rol='Lector')
        ]
        db.session.add_all(usuarios)
        db.session.commit()

# Rutas de la aplicación
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/estadisticas')
def estadisticas():
    usuarios = Usuario.query.all()
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"]
    registros = [3, 5, 2, 8, 4, 6]
    roles_count = {
        "Administradores": Usuario.query.filter_by(rol='Administrador').count(),
        "Editores": Usuario.query.filter_by(rol='Editor').count(),
        "Lectores": Usuario.query.filter_by(rol='Lector').count()
    }
    return render_template('estadisticas.html',
                           usuarios=usuarios,
                           labels=meses,
                           data=registros,
                           roles=roles_count)

@app.route('/funciones')
def funciones():
    return render_template('funciones.html')

@app.route('/documentacion')
def documentacion():
    return render_template('documentacion.html')

if __name__ == '__main__':
    # Escuchar en todas las interfaces para Docker
    app.run(host='0.0.0.0', port=80)

