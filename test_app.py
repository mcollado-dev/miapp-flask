import pytest
from app import app, db, Usuario
import secrets

# ----------------------------
# Fixture para preparar cliente de prueba con DB real
# ----------------------------
@pytest.fixture
def client():
    """
    Fixture que prepara un cliente de prueba para Flask usando la base de datos real.
    NOTA: Este test afectará la base de datos real, por lo que es recomendable usar un entorno de testing.
    """
    app.config['TESTING'] = True
    # Conectamos a la misma DB real configurada en app.py
    # app.config['SQLALCHEMY_DATABASE_URI'] ya apunta a tu MariaDB real

    with app.app_context():
        # Creamos tablas si no existen
        db.create_all()
        # Insertamos un usuario de prueba si no existe
        if not Usuario.query.filter_by(email='test@example.com').first():
            db.session.add(Usuario(nombre='TestUser', email='test@example.com', rol='Usuario'))
            db.session.commit()

        # Devuelve un cliente de Flask para hacer peticiones
        yield app.test_client()

        # Limpieza opcional: borrar el usuario de prueba
        test_user = Usuario.query.filter_by(email='test@example.com').first()
        if test_user:
            db.session.delete(test_user)
            db.session.commit()

# ----------------------------
# Tests de rutas GET (páginas estáticas)
# ----------------------------
def test_home_page(client):
    """Comprueba que la página principal se carga correctamente"""
    response = client.get('/')
    assert response.status_code == 200

def test_funciones_page(client):
    """Comprueba que la página de funciones responde correctamente"""
    response = client.get('/funciones')
    assert response.status_code == 200

def test_documentacion_page(client):
    """Comprueba que la página de documentación responde correctamente"""
    response = client.get('/documentacion')
    assert response.status_code == 200

def test_detalles_page(client):
    """Comprueba que la página de detalles responde correctamente"""
    response = client.get('/detalles')
    assert response.status_code == 200

def test_estadisticas_page(client):
    """Comprueba que la página de estadísticas carga correctamente"""
    response = client.get('/estadisticas')
    assert response.status_code == 200
    assert b'Numero de usuarios' in response.data

# ----------------------------
# Tests de registro de usuarios
# ----------------------------
def test_registro_get(client):
    """Verifica que la página de registro se carga con GET"""
    response = client.get('/registro')
    assert response.status_code == 200
    assert b'Registrar nuevo usuario' in response.data

def test_registro_post_success(client):
    """Registro POST válido y redirección a estadísticas"""
    with client.session_transaction() as session:
        token = secrets.token_hex(16)
        session['csrf_token'] = token

    data = {
        'nombre': 'UsuarioPrueba',
        'email': 'usuario_prueba@example.com',
        'rol': 'Usuario',
        'csrf_token': token
    }
    response = client.post('/registro', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Numero de usuarios' in response.data

    # Limpieza: eliminar el usuario de prueba
    usuario = Usuario.query.filter_by(email='usuario_prueba@example.com').first()
    if usuario:
        db.session.delete(usuario)
        db.session.commit()

def test_registro_post_missing_fields(client):
    """Registro con campos vacíos produce error"""
    with client.session_transaction() as session:
        session['csrf_token'] = 'token123'

    data = {'nombre': '', 'email': '', 'rol': '', 'csrf_token': 'token123'}
    response = client.post('/registro', data=data)
    assert b'Todos los campos son obligatorios.' in response.data

def test_registro_post_invalid_csrf(client):
    """Registro con CSRF inválido produce error"""
    with client.session_transaction() as session:
        session['csrf_token'] = 'token_correcto'

    data = {'nombre': 'User', 'email': 'user@example.com', 'rol': 'Usuario', 'csrf_token': 'token_incorrecto'}
    response = client.post('/registro', data=data)
    assert b'Solicitud inv\xc3\xa1lida' in response.data

# ----------------------------
# Tests de login
# ----------------------------
def test_login_post_success(client):
    """Login válido con usuario existente"""
    with client.session_transaction() as session:
        session['csrf_token'] = 'token123'

    data = {'nombre': 'TestUser', 'email': 'test@example.com', 'csrf_token': 'token123'}
    response = client.post('/login', data=data)
    assert b'Bienvenido, TestUser' in response.data

def test_login_post_user_not_found(client):
    """Login con usuario inexistente produce error"""
    with client.session_transaction() as session:
        session['csrf_token'] = 'token123'

    data = {'nombre': 'NoExiste', 'email': 'noexiste@example.com', 'csrf_token': 'token123'}
    response = client.post('/login', data=data)
    assert b'Usuario no encontrado' in response.data

def test_login_post_missing_fields(client):
    """Login con campos vacíos produce error"""
    with client.session_transaction() as session:
        session['csrf_token'] = 'token123'

    data = {'nombre': '', 'email': '', 'csrf_token': 'token123'}
    response = client.post('/login', data=data)
    assert b'Debes rellenar todos los campos.' in response.data

def test_login_post_invalid_csrf(client):
    """Login con CSRF inválido produce error"""
    with client.session_transaction() as session:
        session['csrf_token'] = 'token_correcto'

    data = {'nombre': 'TestUser', 'email': 'test@example.com', 'csrf_token': 'token_incorrecto'}
    response = client.post('/login', data=data)
    assert b'Solicitud inv\xc3\xa1lida' in response.data

