import pytest
from app import app # This imports your new Flask web server!

@pytest.fixture
def client():
    # This creates a fake "web browser" so pytest can click around your app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test that the /health endpoint returns a 200 OK and says healthy"""
    response = client.get('/health')
    
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
    assert 'pod' in response.json

def test_home_page(client):
    """Test that the main UI page loads successfully"""
    response = client.get('/')
    
    assert response.status_code == 200
    # Checks if our cool HTML UI is actually rendering
    assert b"Deployment Successful" in response.data