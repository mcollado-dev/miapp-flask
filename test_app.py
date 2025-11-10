import pytest
from app import app, db, Usuario
import secrets
import re

# ----------------------------
# Fixture para preparar cliente de prueba con DB real
# ----------------------------
@pytest.fixture
def client():
    """
    Fixture de Pytest que prepara un cliente de prueba de Flask.
    Inserta un usuario de prueba para login y estadísticas.
    """
    app.config['TESTING'] = True

    with app.app_context():
        # Creamos todas las tablas si no existen
        db.create_all()

        # Insertamos un usuario de prueba si no existe
        if not Usuario.query.filter_by(email='test@example.com').first():
            db.session.add(Usuario(nombre='TestUser', email='test@example.com', rol='Usuario'))
            db.session.commit()

        # Cliente de Flask para hacer requests
        yield app.test_client()

        # Limpieza: eliminar usuarios de prueba
        Usuario.query.filter(Usuario.email.in_(['test@example.com', 'usuario_prueba@example.com'])).delete()
        db.session.commit()

# ----------------------------
# Tests de rutas GET (páginas estáticas)
# ----------------------------
def test_home_page(client):
    """Página de inicio carga correctamente"""
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert "Bienvenido" in html or "Inicio" in html

def test_funciones_page(client):
    """Página de funciones carga correctamente"""
    response = client.get('/funciones')
    assert response.status_code == 200

def test_documentacion_page(client):
    """Página de documentación carga correctamente"""
    response = client.get('/documentacion')
    assert response.status_code == 200

def test_detalles_page(client):
    """Página de detalles carga correctamente"""
    response = client.get('/detalles')
    assert response.status_code == 200

# ----------------------------
# Tests de la página de estadísticas
# ----------------------------
def test_estadisticas_page(client):
    """Comprueba que la página de estadísticas muestra el total y usuario de prueba"""
    response = client.get('/estadisticas')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    # Texto exacto que aparece en la plantilla
    assert "Total de usuarios" in html
    assert "TestUser" in html

def test_grafico_roles(client):
    """Comprueba que el gráfico de roles se genera en base64"""
    response = client.get('/estadisticas')
    html = response.data.decode('utf-8')
    # Buscar el <img> del gráfico
    assert 'data:image/png;base64,' in html
    match = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)"', html)
    assert match is not None
    grafico_base64 = match.group(1)
    assert len(grafico_base64) > 100  # Debe contener datos significativos

# ----------------------------
# Tests de registro de usuarios
# ----------------------------
def test_registro_get(client):
    """Página de registro carga correctamente con GET"""
    response = client.get('/registro')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert "Registrar nuevo usuario" in html

def test_registro_post_success(client):
    """Registro POST válido funciona y redirige a estadísticas"""
    with client.session_transaction() as session:
        session['csrf_token'] = secrets.token_hex(16)

    data = {
        'nombre': 'UsuarioPrueba',
        'email': 'usuario_prueba@example.com',
        'rol': 'Usuario',
        'csrf_token': session['csrf_token']
    }
    response = client.post('/registro', data=data, follow_redirects=True)
    html = response.data.decode('utf-8')
    assert response.status_code == 200
    assert "Total de usuarios" in html
    assert "UsuarioPrueba" in html

def test_registro_post_missing_fields(client):
    """Registro con campos vacíos produce error"""
    with client.session_transaction() as session:
        session['csrf_token'] = 'token123'
    data = {'nombre': '', 'email': '', 'rol': '', 'csrf_token': 'token123'}
    response = client.post('/registro', data=data)
    html = response.data.decode('utf-8')
    assert "Todos los campos son obligatorios." in html

# ----------------------------
# Tests de login
# ----------------------------
def test_login_get(client):
    """Página de login carga correctamente"""
    response = client.get('/login')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert "Iniciar sesión" in html

def test_login_post_success(client):
    """Login válido muestra mensaje de bienvenida"""
    with client.session_transaction() as session:
        session['csrf_token'] = 'token123'

    data = {'nombre': 'TestUser', 'email': 'test@example.com', 'csrf_token': 'token123'}
    response = client.post('/login', data=data)
    html = response.data.decode('utf-8')
    assert "Bienvenido, TestUser" in html

def test_login_post_user_not_found(client):
    """Login con usuario inexistente muestra error"""
    with client.session_transaction() as session:
        session['csrf_token'] = 'token123'

    data = {'nombre': 'NoExiste', 'email': 'noexiste@example.com', 'csrf_token': 'token123'}
    response = client.post('/login', data=data)
    html = response.data.decode('utf-8')
    assert "Usuario no encontrado" in html

def test_login_post_missing_fields(client):
    """Login con campos vacíos produce error"""
    with client.session_transaction() as session:
        session['csrf_token'] = 'token123'

    data = {'nombre': '', 'email': '', 'csrf_token': 'token123'}
    response = client.post('/login', data=data)
    html = response.data.decode('utf-8')
    assert "Debes rellenar todos los campos." in html


