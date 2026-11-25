from datetime import datetime, timezone
from decimal import Decimal
from threading import RLock

import pytest

from app.bll.cinema import CinemaError, CinemaService


class StubRepository:
    def __init__(self):
        self.lock = RLock()
        self.booked = {2}

    def movie(self, movie_id):
        if movie_id == 1:
            return {"duration_min": 90}

    def sessions(self):
        return [self.session(1)]

    def session(self, session_id):
        if session_id == 1:
            return {
                "id": 1, "movie_id": 1, "hall": 1, "booked": self.booked,
                "start_time": datetime(2027, 1, 15, 18, tzinfo=timezone.utc),
                "price": Decimal("1500"),
            }

    def reserve(self, session_id, seats):
        self.booked.update(seats)


@pytest.fixture
def service():
    return CinemaService(StubRepository())


@pytest.mark.parametrize("duration", [29, 301])
def test_invalid_duration(service, duration):
    with pytest.raises(CinemaError) as error:
        service.add_movie("Фильм", duration)
    assert error.value.status == 400


def test_overlapping_sessions(service):
    with pytest.raises(CinemaError) as error:
        service.add_session(1, 1, datetime(2027, 1, 15, 19), Decimal("1500"))
    assert error.value.status == 409


def test_book_returns_total_and_removes_seats(service):
    assert service.book(1, [3, 4]) == Decimal("3000")
    assert service.free_seats(1) == [1, *range(5, 51)]


def test_conflict_leaves_other_seat_free(service):
    with pytest.raises(CinemaError) as error:
        service.book(1, [2, 3])
    assert error.value.status == 409
    assert 3 in service.free_seats(1)


@pytest.mark.parametrize("seats", [[], [0], [51], [3, 3]])
def test_invalid_seats(service, seats):
    with pytest.raises(CinemaError) as error:
        service.book(1, seats)
    assert error.value.status == 400
