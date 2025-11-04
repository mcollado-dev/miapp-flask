import pytest
from app import app, db, Usuario

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        db.session.add(Usuario(nombre='TestUser', email='test@example.com', rol='Usuario'))
        db.session.commit()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_estadisticas_page(client):
    response = client.get('/estadisticas')
    assert response.status_code == 200
    assert b'Total de usuarios' in response.data

def test_funciones_page(client):
    response = client.get('/funciones')
    assert response.status_code == 200

def test_documentacion_page(client):
    response = client.get('/documentacion')
    assert response.status_code == 200
