from flask import Flask, render_template
from models import db, Usuario

app = Flask(__name__)

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///miapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db.init_app(app)

@app.before_first_request
def crear_tablas():
    db.create_all()
    if Usuario.query.count() == 0:
        ejemplo = [
            Usuario(nombre='Manuel Collado', email='manuel@example.com'),
            Usuario(nombre='Laura Pérez', email='laura@example.com'),
            Usuario(nombre='Carlos Gómez', email='carlos@example.com')
        ]
        db.session.add_all(ejemplo)
        db.session.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/estadisticas')
def estadisticas():
    usuarios = Usuario.query.all()

    # Datos simulados para gráfico de barras
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"]
    registros = [3, 5, 2, 8, 4, 6]

    # Datos simulados para gráfico circular
    roles = {
        "Administradores": 2,
        "Editores": 5,
        "Lectores": 3
    }

    return render_template(
        'estadisticas.html',
        usuarios=usuarios,
        labels=meses,
        data=registros,
        roles=roles
    )

@app.route('/funciones')
def funciones():
    return render_template('funciones.html')

@app.route('/documentacion')
def documentacion():
    return render_template('documentacion.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)





