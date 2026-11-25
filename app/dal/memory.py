from threading import Lock


class MemoryRepository:
    def __init__(self):
        self.lock = Lock()
        self._movies = {}
        self._sessions = {}

    def movies(self):
        return list(self._movies.values())

    def movie(self, movie_id):
        return self._movies.get(movie_id)

    def add_movie(self, title, duration_min):
        movie_id = len(self._movies) + 1
        movie = {"id": movie_id, "title": title, "duration_min": duration_min}
        self._movies[movie_id] = movie
        return movie

    def sessions(self):
        return list(self._sessions.values())

    def session(self, session_id):
        return self._sessions.get(session_id)

    def add_session(self, movie_id, hall, start_time, price):
        session_id = len(self._sessions) + 1
        session = {
            "id": session_id, "movie_id": movie_id, "hall": hall,
            "start_time": start_time, "price": price, "booked": set(),
        }
        self._sessions[session_id] = session
        return session

    def reserve(self, session_id, seats):
        self._sessions[session_id]["booked"].update(seats)
