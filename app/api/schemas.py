from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, StrictInt


class MovieInput(BaseModel):
    title: str
    duration_min: StrictInt


class MovieOutput(MovieInput):
    id: int


class SessionInput(BaseModel):
    movie_id: StrictInt
    hall: StrictInt
    start_time: datetime
    price: Decimal


class SessionOutput(SessionInput):
    id: int
    price: float


class BookingInput(BaseModel):
    seats: list[StrictInt]


class BookingOutput(BaseModel):
    amount: float
