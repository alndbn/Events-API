import requests
import time
BASE_URL = "http://127.0.0.1:5001"


def test_health_endpoint_returns_healthy():
    response = requests.get(f"{BASE_URL}/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_register_user_creates_new_user():
    username = f"testuser_{int(time.time())}"
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": username,
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["username"] == username


def test_login_returns_jwt_token():
    username = f"loginuser_{int(time.time())}"
    requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": username,
        "password": "password123"
    })
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": username,
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def get_token():
    username = f"eventuser_{int(time.time())}"
    requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": username,
        "password": "password123"
    })
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": username,
        "password": "password123"
    })
    return response.json()["access_token"]


def test_create_public_event_requires_auth_and_succeeds_with_token():
    token = get_token()
    response = requests.post(f"{BASE_URL}/api/events", json={
        "title": "Test Event",
        "description": "Ein Test Event",
        "date": "2027-01-15T18:00:00",
        "is_public": True,
        "requires_admin": False
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Event"


def test_rsvp_to_public_event():
    token = get_token()
    event_response = requests.post(f"{BASE_URL}/api/events", json={
        "title": "RSVP Test Event",
        "description": "Ein öffentliches Event",
        "date": "2027-02-15T18:00:00",
        "is_public": True,
        "requires_admin": False
    }, headers={"Authorization": f"Bearer {token}"})
    event_id = event_response.json()["id"]

    response = requests.post(f"{BASE_URL}/api/rsvps/event/{event_id}", json={
        "attending": True
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201

#-----------------------

def test_duplicate_registration_returns_400():
    username = f"dupuser_{int(time.time())}"
    requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": username,
        "password": "password123"
    })
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": username,
        "password": "password123"
    })
    assert response.status_code == 400


def test_create_event_without_auth_returns_401():
    response = requests.post(f"{BASE_URL}/api/events", json={
        "title": "Unauthorized Event",
        "description": "Sollte nicht funktionieren",
        "date": "2027-03-15T18:00:00",
        "is_public": True
    })
    assert response.status_code == 401


def test_rsvp_to_non_public_event_without_auth_returns_401():
    token = get_token()
    event_response = requests.post(f"{BASE_URL}/api/events", json={
        "title": "Private Event",
        "description": "Nicht öffentlich",
        "date": "2027-04-15T18:00:00",
        "is_public": False,
        "requires_admin": False
    }, headers={"Authorization": f"Bearer {token}"})
    event_id = event_response.json()["id"]

    response = requests.post(f"{BASE_URL}/api/rsvps/event/{event_id}", json={
        "attending": True
    })
    assert response.status_code == 401