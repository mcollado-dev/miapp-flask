# Importamos la clase SQLAlchemy, que nos permite trabajar con bases de datos de forma sencilla en Flask
from flask_sqlalchemy import SQLAlchemy

# Creamos una instancia global de SQLAlchemy para usarla en toda la aplicación
db = SQLAlchemy()

# Definimos el modelo "Usuario", que representa una tabla en la base de datos
class Usuario(db.Model):
    # Campo 'id': clave primaria de tipo entero (única por usuario)
    id = db.Column(db.Integer, primary_key=True)

    # Campo 'nombre': texto obligatorio (no puede ser nulo)
    nombre = db.Column(db.String(80), nullable=False)

    # Campo 'email': texto obligatorio y único (no puede repetirse entre usuarios)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Campo 'rol': texto obligatorio con valor por defecto 'Lector'
    rol = db.Column(db.String(50), nullable=False, default='Lector')

    # Campo 'password_hash': contraseña hasheada (nunca se guarda en texto plano)
    password_hash = db.Column(db.String(255), nullable=True)

    # Representación legible del objeto, útil para depuración o consola
    def __repr__(self):
        return f'<Usuario {self.nombre}>'




