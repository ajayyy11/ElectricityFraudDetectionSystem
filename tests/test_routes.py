import pytest

def test_home_redirect(client):
    # Should redirect to login if not authenticated
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.location

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_404_error(client):
    response = client.get('/non-existent-page')
    assert response.status_code == 404
    assert b'Page Not Found' in response.data
