from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TripStatus = Literal[
    "requested",
    "accepted",
    "in_progress",
    "completed",
    "cancelled",
]

TripSource = Literal[
    "manual",
    "notification",
    "integration",
]


class TripCreate(BaseModel):
    driver_id: int = Field(gt=0)
    vehicle_id: int | None = Field(default=None, gt=0)
    platform_id: int = Field(gt=0)

    pickup_address: str | None = Field(default=None, max_length=255)
    dropoff_address: str | None = Field(default=None, max_length=255)

    # Coordenadas em graus decimais (WGS 84).
    pickup_latitude: float | None = Field(default=None, ge=-90, le=90)
    pickup_longitude: float | None = Field(default=None, ge=-180, le=180)
    dropoff_latitude: float | None = Field(default=None, ge=-90, le=90)
    dropoff_longitude: float | None = Field(default=None, ge=-180, le=180)

    pickup_distance_km: Decimal = Field(default=Decimal("0.00"), ge=0)
    trip_distance_km: Decimal = Field(default=Decimal("0.00"), ge=0)

    fare_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    tip_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    platform_fee_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    tolls_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    parking_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    fuel_cost_amount: Decimal = Field(default=Decimal("0.00"), ge=0)
    other_expenses_amount: Decimal = Field(default=Decimal("0.00"), ge=0)

    status: TripStatus = "requested"
    source: TripSource = "manual"

    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None


class TripUpdate(BaseModel):
    vehicle_id: int | None = Field(default=None, gt=0)

    pickup_address: str | None = Field(default=None, max_length=255)
    dropoff_address: str | None = Field(default=None, max_length=255)

    pickup_latitude: float | None = Field(default=None, ge=-90, le=90)
    pickup_longitude: float | None = Field(default=None, ge=-180, le=180)
    dropoff_latitude: float | None = Field(default=None, ge=-90, le=90)
    dropoff_longitude: float | None = Field(default=None, ge=-180, le=180)

    pickup_distance_km: Decimal | None = Field(default=None, ge=0)
    trip_distance_km: Decimal | None = Field(default=None, ge=0)

    fare_amount: Decimal | None = Field(default=None, ge=0)
    tip_amount: Decimal | None = Field(default=None, ge=0)
    platform_fee_amount: Decimal | None = Field(default=None, ge=0)
    tolls_amount: Decimal | None = Field(default=None, ge=0)
    parking_amount: Decimal | None = Field(default=None, ge=0)
    fuel_cost_amount: Decimal | None = Field(default=None, ge=0)
    other_expenses_amount: Decimal | None = Field(default=None, ge=0)

    status: TripStatus | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None


class TripRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    driver_id: int
    vehicle_id: int | None
    platform_id: int

    pickup_address: str | None
    dropoff_address: str | None

    pickup_distance_km: Decimal
    trip_distance_km: Decimal

    fare_amount: Decimal
    tip_amount: Decimal
    platform_fee_amount: Decimal
    tolls_amount: Decimal
    parking_amount: Decimal
    fuel_cost_amount: Decimal
    other_expenses_amount: Decimal

    status: str
    source: str

    requested_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    notes: str | None
