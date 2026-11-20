
from sqlalchemy import func
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement

from backend.app.models.trip import Trip
from backend.app.models.trip_location import TripLocation
from backend.app.schemas.trip_location import TripLocationCreate


def record_trip_location(
    db: Session,
    trip_id: int,
    location_data: TripLocationCreate,
) -> dict:
    trip = db.get(Trip, trip_id)

    if trip is None:
        raise ValueError("Corrida não encontrada.")

    location = WKTElement(
        f"POINT({location_data.longitude} {location_data.latitude})",
        srid=4326,
    )

    location_values = location_data.model_dump(
        exclude={"latitude", "longitude", "recorded_at"},
    )

    trip_location = TripLocation(
        trip_id=trip_id,
        location=location,
        **location_values,
    )

    if location_data.recorded_at is not None:
        trip_location.recorded_at = location_data.recorded_at

    db.add(trip_location)
    db.commit()
    db.refresh(trip_location)

    latitude, longitude = db.query(
        func.ST_Y(TripLocation.location),
        func.ST_X(TripLocation.location),
    ).filter(
        TripLocation.id == trip_location.id
    ).one()

    return {
        "id": trip_location.id,
        "trip_id": trip_location.trip_id,
        "latitude": latitude,
        "longitude": longitude,
        "recorded_at": trip_location.recorded_at,
        "speed_kmh": trip_location.speed_kmh,
        "accuracy_m": trip_location.accuracy_m,
        "heading_degrees": trip_location.heading_degrees,
    }


def list_trip_locations(
    db: Session,
    trip_id: int,
) -> list[dict]:
    results = (
        db.query(
            TripLocation,
            func.ST_Y(TripLocation.location).label("latitude"),
            func.ST_X(TripLocation.location).label("longitude"),
        )
        .filter(TripLocation.trip_id == trip_id)
        .order_by(TripLocation.recorded_at.asc())
        .all()
    )

    return [
        {
            "id": location.id,
            "trip_id": location.trip_id,
            "latitude": latitude,
            "longitude": longitude,
            "recorded_at": location.recorded_at,
            "speed_kmh": location.speed_kmh,
            "accuracy_m": location.accuracy_m,
            "heading_degrees": location.heading_degrees,
        }
        for location, latitude, longitude in results
    ]
