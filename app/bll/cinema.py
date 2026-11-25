from datetime import timedelta, timezone


class CinemaError(Exception):
    def __init__(self, status, detail):
        super().__init__(detail)
        self.status = status
        self.detail = detail


class CinemaService:
    def __init__(self, repository):
        self.repository = repository

    def movies(self):
        with self.repository.lock:
            return self.repository.movies()

    def add_movie(self, title, duration_min):
        if not 30 <= duration_min <= 300:
            raise CinemaError(400, "duration_min must be between 30 and 300")
        with self.repository.lock:
            return self.repository.add_movie(title, duration_min)

    @staticmethod
    def public_session(session):
        return {key: value for key, value in session.items() if key != "booked"}

    def sessions(self, movie_id=None):
        with self.repository.lock:
            return [
                self.public_session(session)
                for session in self.repository.sessions()
                if movie_id is None or session["movie_id"] == movie_id
            ]

    def add_session(self, movie_id, hall, start_time, price):
        if not 1 <= hall <= 5:
            raise CinemaError(400, "hall must be between 1 and 5")
        if not price.is_finite() or price <= 0:
            raise CinemaError(400, "price must be positive")

        # Время без часового пояса считаем временем UTC.
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        with self.repository.lock:
            movie = self.repository.movie(movie_id)
            if movie is None:
                raise CinemaError(404, "Movie not found")
            end_time = start_time + timedelta(minutes=movie["duration_min"])
            for existing in self.repository.sessions():
                if existing["hall"] != hall:
                    continue
                existing_movie = self.repository.movie(existing["movie_id"])
                existing_start = existing["start_time"]
                existing_end = existing_start + timedelta(minutes=existing_movie["duration_min"])
                if start_time < existing_end and existing_start < end_time:
                    raise CinemaError(409, "Sessions overlap in the same hall")
            session = self.repository.add_session(movie_id, hall, start_time, price)
            return self.public_session(session)

    def _session(self, session_id):
        session = self.repository.session(session_id)
        if session is None:
            raise CinemaError(404, "Session not found")
        return session

    def free_seats(self, session_id):
        with self.repository.lock:
            session = self._session(session_id)
            return [seat for seat in range(1, 51) if seat not in session["booked"]]

    def book(self, session_id, seats):
        if not seats or any(not 1 <= seat <= 50 for seat in seats):
            raise CinemaError(400, "Choose seats between 1 and 50")
        if len(set(seats)) != len(seats):
            raise CinemaError(400, "Seat numbers must be unique")
        with self.repository.lock:
            session = self._session(session_id)
            if session["booked"].intersection(seats):
                raise CinemaError(409, "A selected seat is already booked")
            self.repository.reserve(session_id, seats)
            return len(seats) * session["price"]
