from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TripLocationCreate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    recorded_at: datetime | None = None
    speed_kmh: Decimal | None = Field(default=None, ge=0, le=500)
    accuracy_m: Decimal | None = Field(default=None, ge=0)
    heading_degrees: Decimal | None = Field(default=None, ge=0, lt=360)


class TripLocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_id: int
    latitude: float
    longitude: float
    recorded_at: datetime
    speed_kmh: Decimal | None
    accuracy_m: Decimal | None
    heading_degrees: Decimal | None
