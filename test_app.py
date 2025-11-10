import pytest
from app import app, db, Usuario
import secrets
import re

# ----------------------------
# Fixture: cliente de prueba usando la DB real
# ----------------------------
@pytest.fixture
def client():
    """
    Prepara un cliente de prueba de Flask.
    Inserta un usuario de prueba para login y estadísticas.
    """
    app.config['TESTING'] = True

    with app.app_context():
        # Crear todas las tablas si no existen
        db.create_all()

        # Insertar usuario de prueba si no existe
        if not Usuario.query.filter_by(email='test@example.com').first():
            db.session.add(Usuario(nombre='TestUser', email='test@example.com', rol='Usuario'))
            db.session.commit()

        # Proporcionar cliente Flask para tests
        yield app.test_client()

        # Limpieza: borrar usuarios de prueba añadidos durante los tests
        Usuario.query.filter(Usuario.email.in_(['test@example.com', 'usuario_prueba@example.com'])).delete()
        db.session.commit()

# ----------------------------
# Tests de páginas GET
# ----------------------------
def test_home_page(client):
    """Comprobar que la página de inicio carga correctamente"""
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert "Inicio" in html or "Bienvenido" in html

def test_funciones_page(client):
    """Comprobar que la página de funciones carga correctamente"""
    response = client.get('/funciones')
    assert response.status_code == 200

def test_documentacion_page(client):
    """Comprobar que la página de documentación carga correctamente"""
    response = client.get('/documentacion')
    assert response.status_code == 200

def test_detalles_page(client):
    """Comprobar que la página de detalles carga correctamente"""
    response = client.get('/detalles')
    assert response.status_code == 200

# ----------------------------
# Tests de estadísticas
# ----------------------------
def test_estadisticas_page(client):
    """Comprobar que la página de estadísticas muestra el total y usuario de prueba"""
    response = client.get('/estadisticas')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert "Total de usuarios" in html
    assert "TestUser" in html

def test_grafico_roles(client):
    """Comprobar que el gráfico de roles se genera en base64"""
    response = client.get('/estadisticas')
    html = response.data.decode('utf-8')
    assert 'data:image/png;base64,' in html
    match = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)"', html)
    assert match is not None
    grafico_base64 = match.group(1)
    # Debe contener datos significativos
    assert len(grafico_base64) > 100

# ----------------------------
# Tests de registro
# ----------------------------
def test_registro_get(client):
    """Comprobar que la página de registro carga con GET"""
    response = client.get('/registro')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert "Registrar nuevo usuario" in html

def test_registro_post_success(client):
    """Registro POST válido funciona y redirige a estadísticas"""
    # Hacer GET primero para generar CSRF en sesión
    client.get('/registro')
    with client.session_transaction() as session:
        csrf_token = session['csrf_token']  # Recuperar el token generado

    # Datos válidos de registro
    data = {
        'nombre': 'UsuarioPrueba',
        'email': 'usuario_prueba@example.com',
        'rol': 'Usuario',
        'csrf_token': csrf_token
    }

    # POST al endpoint de registro
    response = client.post('/registro', data=data, follow_redirects=True)
    html = response.data.decode('utf-8')
    assert response.status_code == 200
    assert "Total de usuarios" in html
    assert "UsuarioPrueba" in html

def test_registro_post_missing_fields(client):
    """Registro con campos vacíos produce error"""
    client.get('/registro')
    with client.session_transaction() as session:
        csrf_token = session['csrf_token']

    data = {'nombre': '', 'email': '', 'rol': '', 'csrf_token': csrf_token}
    response = client.post('/registro', data=data)
    html = response.data.decode('utf-8')
    assert "Todos los campos son obligatorios." in html

def test_registro_post_invalid_csrf(client):
    """Registro con CSRF inválido produce error"""
    client.get('/registro')
    data = {'nombre': 'X', 'email': 'x@x.com', 'rol': 'Usuario', 'csrf_token': 'token_invalido'}
    response = client.post('/registro', data=data)
    html = response.data.decode('utf-8')
    assert "Solicitud inválida." in html

# ----------------------------
# Tests de login
# ----------------------------
def test_login_get(client):
    """Comprobar que la página de login carga correctamente"""
    response = client.get('/login')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert "Iniciar sesión" in html

def test_login_post_success(client):
    """Login válido muestra mensaje de bienvenida"""
    client.get('/login')  # GET para generar CSRF
    with client.session_transaction() as session:
        csrf_token = session['csrf_token']

    data = {'nombre': 'TestUser', 'email': 'test@example.com', 'csrf_token': csrf_token}
    response = client.post('/login', data=data)
    html = response.data.decode('utf-8')
    assert "Bienvenido, TestUser" in html

def test_login_post_user_not_found(client):
    """Login con usuario inexistente muestra error"""
    client.get('/login')
    with client.session_transaction() as session:
        csrf_token = session['csrf_token']

    data = {'nombre': 'NoExiste', 'email': 'noexiste@example.com', 'csrf_token': csrf_token}
    response = client.post('/login', data=data)
    html = response.data.decode('utf-8')
    assert "Usuario no encontrado" in html

def test_login_post_missing_fields(client):
    """Login con campos vacíos produce error"""
    client.get('/login')
    with client.session_transaction() as session:
        csrf_token = session['csrf_token']

    data = {'nombre': '', 'email': '', 'csrf_token': csrf_token}
    response = client.post('/login', data=data)
    html = response.data.decode('utf-8')
    assert "Debes rellenar todos los campos." in html

def test_login_post_invalid_csrf(client):
    """Login con CSRF inválido produce error"""
    client.get('/login')
    data = {'nombre': 'TestUser', 'email': 'test@example.com', 'csrf_token': 'token_invalido'}
    response = client.post('/login', data=data)
    html = response.data.decode('utf-8')
    assert "Solicitud inválida." in html




