import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def session_data(client):
    movie = client.post("/movies", json={"title": "Фильм", "duration_min": 90})
    assert movie.status_code == 201
    return {
        "movie_id": movie.json()["id"], "hall": 1,
        "start_time": "2027-01-15T18:00:00+05:00", "price": 1500,
    }


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_list_movies(client, session_data):
    movies = client.get("/movies").json()
    assert movies == [{"id": session_data["movie_id"], "title": "Фильм", "duration_min": 90}]


def test_invalid_movie(client):
    response = client.post("/movies", json={"title": "Фильм", "duration_min": 301})
    assert response.status_code == 400


@pytest.mark.parametrize("update", [{"hall": 6}, {"price": 0}, {"price": -1}])
def test_invalid_session(client, session_data, update):
    response = client.post("/sessions", json=session_data | update)
    assert response.status_code == 400


def test_filter_sessions(client, session_data):
    session = client.post("/sessions", json=session_data)
    assert session.status_code == 201
    assert client.get("/sessions", params={"movie_id": session_data["movie_id"]}).json() == [session.json()]
    assert client.get("/sessions", params={"movie_id": 999}).json() == []


def test_overlap_and_adjacent_sessions(client, session_data):
    assert client.post("/sessions", json=session_data).status_code == 201
    assert client.post("/sessions", json=session_data).status_code == 409
    adjacent = session_data | {"start_time": "2027-01-15T19:30:00+05:00"}
    assert client.post("/sessions", json=adjacent).status_code == 201


def test_booking_and_conflict(client, session_data):
    session = client.post("/sessions", json=session_data).json()
    path = f"/sessions/{session['id']}"
    assert client.get(f"{path}/seats").json() == list(range(1, 51))
    booking = client.post(f"{path}/book", json={"seats": [3, 4]})
    assert booking.status_code == 200
    assert booking.json() == {"amount": 3000}
    assert 3 not in client.get(f"{path}/seats").json()
    assert client.post(f"{path}/book", json={"seats": [4]}).status_code == 409
