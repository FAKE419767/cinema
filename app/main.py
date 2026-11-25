import os
from datetime import datetime
from decimal import Decimal

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.routes import cinema_router
from app.bll.cinema import CinemaError, CinemaService
from app.dal.memory import MemoryRepository


def create_app(seed_demo=False):
    service = CinemaService(MemoryRepository())
    if seed_demo:
        demo = [
            ("Дорога к звёздам", 110, 1, "18:00", "1500"),
            ("Ночной экспресс", 95, 2, "19:00", "1800"),
            ("Летний дождь", 85, 3, "20:00", "1200"),
        ]
        for title, duration, hall, time, price in demo:
            movie = service.add_movie(title, duration)
            start = datetime.fromisoformat(f"2027-01-15T{time}:00+05:00")
            service.add_session(movie["id"], hall, start, Decimal(price))

    app = FastAPI(title="Кинотеатр")

    @app.exception_handler(CinemaError)
    async def cinema_error(request, error):
        return JSONResponse(status_code=error.status, content={"detail": error.detail})

    app.include_router(cinema_router(service))
    return app


app = create_app(seed_demo=os.getenv("CINEMA_DEMO") == "1")
