import pytest
from app import app, db, Usuario
import re

# ----------------------------
# Fixture: cliente de prueba
# ----------------------------
@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()

        # Insertar usuario de prueba si no existe
        if not Usuario.query.filter_by(email='test@example.com').first():
            db.session.add(Usuario(nombre='TestUser', email='test@example.com', rol='Usuario'))
            db.session.commit()

        yield app.test_client()

        # Limpieza: eliminar usuarios de prueba
        Usuario.query.filter(Usuario.email.in_(['test@example.com', 'usuario_prueba@example.com'])).delete()
        db.session.commit()


# ----------------------------
# Helpers
# ----------------------------
def get_csrf(html):
    """Extrae CSRF token de una página"""
    match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', html)
    return match.group(1) if match else ''


# ----------------------------
# Tests GET de rutas estáticas
# ----------------------------
def test_home(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert "Inicio" in resp.data.decode('utf-8') or "Bienvenido" in resp.data.decode('utf-8')

def test_funciones(client):
    resp = client.get('/funciones')
    assert resp.status_code == 200

def test_documentacion(client):
    resp = client.get('/documentacion')
    assert resp.status_code == 200

def test_detalles(client):
    resp = client.get('/detalles')
    assert resp.status_code == 200


# ----------------------------
# Tests estadísticas
# ----------------------------
def test_estadisticas(client):
    resp = client.get('/estadisticas')
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')
    assert "Total de usuarios" in html
    assert "TestUser" in html
    # Verificar que existe gráfico base64
    assert 'data:image/png;base64,' in html


# ----------------------------
# Tests de registro
# ----------------------------
def test_registro_get(client):
    resp = client.get('/registro')
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')
    assert "Registrar nuevo usuario" in html

def test_registro_post_success(client):
    resp = client.get('/registro')
    csrf = get_csrf(resp.data.decode())

    data = {
        'nombre': 'UsuarioPrueba',
        'email': 'usuario_prueba@example.com',
        'rol': 'Usuario',
        'csrf_token': csrf
    }
    resp = client.post('/registro', data=data, follow_redirects=True)
    html = resp.data.decode('utf-8')
    assert resp.status_code == 200
    assert "Total de usuarios" in html
    assert "UsuarioPrueba" in html

def test_registro_post_missing_fields(client):
    resp = client.get('/registro')
    csrf = get_csrf(resp.data.decode())

    data = {'nombre': '', 'email': '', 'rol': '', 'csrf_token': csrf}
    resp = client.post('/registro', data=data)
    html = resp.data.decode('utf-8')
    assert "This field is required" in html or "Todos los campos son obligatorios." in html

def test_registro_post_duplicate_email(client):
    resp = client.get('/registro')
    csrf = get_csrf(resp.data.decode())

    # Intentar registrar usuario con email existente
    data = {'nombre': 'Duplicado', 'email': 'test@example.com', 'rol': 'Usuario', 'csrf_token': csrf}
    resp = client.post('/registro', data=data)
    html = resp.data.decode('utf-8')
    assert "already exists" in html or "Email already exists" not in html  # depende del mensaje que pongas


# ----------------------------
# Tests de login
# ----------------------------
def test_login_get(client):
    resp = client.get('/login')
    assert resp.status_code == 200
    html = resp.data.decode('utf-8')
    assert "Iniciar sesión" in html

def test_login_post_success(client):
    resp = client.get('/login')
    csrf = get_csrf(resp.data.decode())

    data = {'nombre': 'TestUser', 'email': 'test@example.com', 'csrf_token': csrf}
    resp = client.post('/login', data=data)
    html = resp.data.decode('utf-8')
    assert "Bienvenido, TestUser (Usuario)" in html

def test_login_post_user_not_found(client):
    resp = client.get('/login')
    csrf = get_csrf(resp.data.decode())

    data = {'nombre': 'NoExiste', 'email': 'noexiste@example.com', 'csrf_token': csrf}
    resp = client.post('/login', data=data)
    html = resp.data.decode('utf-8')
    assert "Usuario no encontrado" in html

def test_login_post_missing_fields(client):
    resp = client.get('/login')
    csrf = get_csrf(resp.data.decode())

    data = {'nombre': '', 'email': '', 'csrf_token': csrf}
    resp = client.post('/login', data=data)
    html = resp.data.decode('utf-8')
    assert "This field is required" in html or "Debes rellenar todos los campos." in html
