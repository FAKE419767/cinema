from fastapi import APIRouter

from app.api.schemas import (
    BookingInput, BookingOutput, MovieInput, MovieOutput, SessionInput, SessionOutput,
)


def cinema_router(service):
    router = APIRouter()

    @router.get("/health")
    def health():
        return {"status": "ok"}

    @router.get("/movies", response_model=list[MovieOutput])
    def movies():
        return service.movies()

    @router.post("/movies", response_model=MovieOutput, status_code=201)
    def add_movie(movie: MovieInput):
        return service.add_movie(movie.title, movie.duration_min)

    @router.get("/sessions", response_model=list[SessionOutput])
    def sessions(movie_id: int | None = None):
        return service.sessions(movie_id)

    @router.post("/sessions", response_model=SessionOutput, status_code=201)
    def add_session(session: SessionInput):
        return service.add_session(session.movie_id, session.hall, session.start_time, session.price)

    @router.get("/sessions/{id}/seats")
    def seats(id: int):
        return service.free_seats(id)

    @router.post("/sessions/{id}/book", response_model=BookingOutput)
    def book(id: int, booking: BookingInput):
        return {"amount": service.book(id, booking.seats)}

    return router
