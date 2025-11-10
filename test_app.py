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
        # Usuario de prueba
        if not Usuario.query.filter_by(email='test@example.com').first():
            db.session.add(Usuario(nombre='TestUser', email='test@example.com', rol='Usuario'))
            db.session.commit()

        yield app.test_client()

        # Limpieza
        Usuario.query.filter(Usuario.email.in_(['test@example.com', 'usuario_prueba@example.com'])).delete()
        db.session.commit()

# ----------------------------
# Tests GET
# ----------------------------
def test_home_page(client):
    resp = client.get('/')
    assert resp.status_code == 200

def test_registro_get(client):
    resp = client.get('/registro')
    assert resp.status_code == 200

def test_login_get(client):
    resp = client.get('/login')
    assert resp.status_code == 200

# ----------------------------
# Tests POST con CSRF
# ----------------------------
def get_csrf(html):
    match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', html)
    return match.group(1) if match else ''

def test_registro_post_success(client):
    resp = client.get('/registro')
    csrf = get_csrf(resp.data.decode())
    data = {'nombre': 'UsuarioPrueba', 'email': 'usuario_prueba@example.com', 'rol':'Usuario', 'csrf_token': csrf}
    resp = client.post('/registro', data=data, follow_redirects=True)
    html = resp.data.decode()
    assert "Total de usuarios" in html
    assert "UsuarioPrueba" in html

def test_login_post_success(client):
    resp = client.get('/login')
    csrf = get_csrf(resp.data.decode())
    data = {'nombre':'TestUser','email':'test@example.com','csrf_token':csrf}
    resp = client.post('/login', data=data)
    html = resp.data.decode()
    assert "Bienvenido, TestUser (Usuario)" in html
