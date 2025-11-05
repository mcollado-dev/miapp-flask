import pytest
from app import app, db, Usuario

# Fixture que prepara un cliente de prueba para Flask
# Crea una base de datos temporal en memoria y añade un usuario de ejemplo.
@pytest.fixture
def client():
    app.config['TESTING'] = True  # Activa el modo de prueba en Flask
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # BD temporal en memoria
    with app.app_context():
        db.create_all()  # Crea las tablas
        # Inserta un usuario de prueba
        db.session.add(Usuario(nombre='TestUser', email='test@example.com', rol='Usuario'))
        db.session.commit()
        # Devuelve un cliente de prueba de Flask para hacer peticiones HTTP simuladas
        yield app.test_client()
        # Limpieza: elimina la sesión y borra todas las tablas
        db.session.remove()
        db.drop_all()

# Test que comprueba que la página principal carga correctamente
def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200  # Verifica que la respuesta sea OK (HTTP 200)

# Test que comprueba que la página de estadísticas funciona y muestra el total de usuarios
def test_estadisticas_page(client):
    response = client.get('/estadisticas')
    assert response.status_code == 200  # Verifica que la página se carga bien
    assert b'Total de usuarios' in response.data  # Comprueba que el texto esperado aparece en la respuesta

# Test que verifica que la página de funciones responde correctamente
def test_funciones_page(client):
    response = client.get('/funciones')
    assert response.status_code == 200

# Test que verifica que la página de documentación responde correctamente
def test_documentacion_page(client):
    response = client.get('/documentacion')
    assert response.status_code == 200
