from flask import Flask, render_template
from models import db, Usuario

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///miapp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Inicializar la base de datos y añadir un usuario de ejemplo si está vacía
with app.app_context():
    db.create_all()
    if Usuario.query.count() == 0:
        demo_user = Usuario(nombre="Admin", email="admin@example.com", rol="Administrador")
        db.session.add(demo_user)
        db.session.commit()

# Rutas
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/estadisticas')
def estadisticas():
    # Ejemplo: puedes calcular estadísticas reales aquí
    usuarios = Usuario.query.all()
    total_usuarios = len(usuarios)
    return render_template('estadisticas.html', total_usuarios=total_usuarios, usuarios=usuarios)

@app.route('/funciones')
def funciones():
    return render_template('funciones.html')

@app.route('/documentacion')
def documentacion():
    return render_template('documentacion.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

