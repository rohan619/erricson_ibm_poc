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
    assert 'uptime_seconds' in response.json

def test_home_page(client):
    """Test that the main UI page loads successfully"""
    response = client.get('/')
    
    assert response.status_code == 200
    assert b"Mission Control Live" in response.data


def test_metrics_endpoint(client):
    response = client.get('/api/metrics')

    assert response.status_code == 200
    payload = response.json
    assert 'cpu' in payload
    assert 'memory' in payload
    assert 'disk' in payload
    assert 'uptime_seconds' in payload
    assert 'requests_served' in payload


def test_history_endpoint(client):
    client.get('/api/metrics')
    response = client.get('/api/history')

    assert response.status_code == 200
    payload = response.json
    assert 'points' in payload
    assert isinstance(payload['points'], list)
    assert len(payload['points']) >= 1


def test_system_endpoint(client):
    response = client.get('/api/system')

    assert response.status_code == 200
    payload = response.json
    assert 'hostname' in payload
    assert 'pod_ip' in payload
    assert 'platform' in payload
    assert 'requests_served' in payload


def test_insights_endpoint(client):
    response = client.get('/api/insights')

    assert response.status_code == 200
    payload = response.json
    assert payload['state'] in {'stable', 'watch', 'critical'}
    assert isinstance(payload['stability_score'], int)
    assert 'current' in payload
