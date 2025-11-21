import pytest
from app import app, db, Usuario
import re
from werkzeug.security import generate_password_hash

# ----------------------------
# Fixture: cliente de prueba
# ----------------------------
@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()
        # Usuario de prueba con contraseña
        if not Usuario.query.filter_by(email='test@example.com').first():
            db.session.add(Usuario(
                nombre='TestUser',
                email='test@example.com',
                rol='Usuario',
                password_hash=generate_password_hash('Prueba1234')
            ))
            db.session.commit()

        yield app.test_client()

        # Limpieza
        Usuario.query.filter(Usuario.email.in_(['test@example.com', 'usuario_prueba@example.com'])).delete()
        db.session.commit()

# ----------------------------
# Helper: obtener CSRF token
# ----------------------------
def get_csrf(html):
    match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', html)
    return match.group(1) if match else ''

# ----------------------------
# Tests GET
# ----------------------------
def test_home_page(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert "Inicio" in resp.data.decode('utf-8') or "Bienvenido" in resp.data.decode('utf-8')

def test_registro_get(client):
    with client.session_transaction() as sess:
        sess['rol'] = 'Administrador'

    resp = client.get('/registro')
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')
    assert "Registrar nuevo usuario" in html

def test_login_get(client):
    resp = client.get('/login')
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')
    assert "Iniciar sesión" in html

# ----------------------------
# Tests POST registro
# ----------------------------
def test_registro_post_success(client):
    with client.session_transaction() as sess:
        sess['rol'] = 'Administrador'

    resp = client.get('/registro')
    csrf = get_csrf(resp.data.decode())
    data = {
        'nombre': 'UsuarioPrueba',
        'email': 'usuario_prueba@example.com',
        'rol': 'Usuario',
        'password': 'Prueba1234',
        'confirmar': 'Prueba1234',
        'csrf_token': csrf
    }
    resp = client.post('/registro', data=data, follow_redirects=True)
    html = resp.data.decode('utf-8')
    assert resp.status_code == 200
    assert "Total de usuarios" in html
    assert "UsuarioPrueba" in html

def test_registro_post_missing_fields(client):
    with client.session_transaction() as sess:
        sess['rol'] = 'Administrador'

    resp = client.get('/registro')
    csrf = get_csrf(resp.data.decode())
    data = {
        'nombre': '',
        'email': '',
        'rol': '',
        'password': '',
        'confirmar': '',
        'csrf_token': csrf
    }
    resp = client.post('/registro', data=data)
    html = resp.data.decode('utf-8')
    assert "This field is required" in html or "Todos los campos son obligatorios." in html

# ----------------------------
# Tests POST login
# ----------------------------
def test_login_post_success(client):
    resp = client.get('/login')
    csrf = get_csrf(resp.data.decode())
    data = {
        'nombre': 'TestUser',
        'email': 'test@example.com',
        'password': 'Prueba1234',
        'csrf_token': csrf
    }
    resp = client.post('/login', data=data)
    html = resp.data.decode('utf-8')
    assert "Bienvenido, TestUser (Usuario)" in html

def test_login_post_user_not_found(client):
    resp = client.get('/login')
    csrf = get_csrf(resp.data.decode())
    data = {
        'nombre': 'NoExiste',
        'email': 'noexiste@example.com',
        'password': 'Cualquier123',
        'csrf_token': csrf
    }
    resp = client.post('/login', data=data)
    html = resp.data.decode('utf-8')
    assert "Usuario o contraseña incorrectos" in html

def test_login_post_missing_fields(client):
    resp = client.get('/login')
    csrf = get_csrf(resp.data.decode())
    data = {
        'nombre': '',
        'email': '',
        'password': '',
        'csrf_token': csrf
    }
    resp = client.post('/login', data=data)
    html = resp.data.decode('utf-8')
    assert "This field is required" in html or "Debes rellenar todos los campos." in html

# ----------------------------
# Tests de otras páginas
# ----------------------------
def test_funciones_page(client):
    resp = client.get('/funciones')
    assert resp.status_code == 200

def test_documentacion_page(client):
    resp = client.get('/documentacion')
    assert resp.status_code == 200

def test_detalles_page(client):
    resp = client.get('/detalles')
    assert resp.status_code == 200

def test_estadisticas_page(client):
    with client.session_transaction() as sess:
        sess['rol'] = 'Administrador'

    resp = client.get('/estadisticas')
    html = resp.data.decode('utf-8')
    assert resp.status_code == 200
    assert "Total de usuarios" in html
    assert "TestUser" in html
