
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement

from backend.app.models.driver import Driver
from backend.app.models.vehicle import Vehicle
from backend.app.models.platform import Platform
from backend.app.models.trip import Trip
from backend.app.schemas.trip import TripCreate, TripUpdate


def create_trip(db: Session, trip_data: TripCreate) -> Trip:
    data = trip_data.model_dump()

    pickup_lat = data.pop("pickup_latitude")
    pickup_lon = data.pop("pickup_longitude")
    dropoff_lat = data.pop("dropoff_latitude")
    dropoff_lon = data.pop("dropoff_longitude")

    if (pickup_lat is None) != (pickup_lon is None):
        raise ValueError("Informe latitude e longitude da origem juntas.")

    if (dropoff_lat is None) != (dropoff_lon is None):
        raise ValueError("Informe latitude e longitude do destino juntas.")

    driver = db.get(Driver, data["driver_id"])
    if driver is None:
        raise ValueError("Motorista não encontrado.")

    platform = db.get(Platform, data["platform_id"])
    if platform is None:
        raise ValueError("Plataforma não encontrada.")

    vehicle_id = data.get("vehicle_id")
    if vehicle_id is not None:
        vehicle = db.get(Vehicle, vehicle_id)
        if vehicle is None or vehicle.driver_id != driver.id:
            raise ValueError("Veículo não encontrado para este motorista.")

    if pickup_lat is not None:
        data["pickup_location"] = WKTElement(
            f"POINT({pickup_lon} {pickup_lat})",
            srid=4326,
        )

    if dropoff_lat is not None:
        data["dropoff_location"] = WKTElement(
            f"POINT({dropoff_lon} {dropoff_lat})",
            srid=4326,
        )

    trip = Trip(**data)
    db.add(trip)
    db.commit()
    db.refresh(trip)

    return trip


def get_trip(db: Session, trip_id: int) -> Trip | None:
    return db.get(Trip, trip_id)


def list_trips(
    db: Session,
    driver_id: int,
    platform_id: int | None = None,
    status: str | None = None,
) -> list[Trip]:
    query = db.query(Trip).filter(Trip.driver_id == driver_id)

    if platform_id is not None:
        query = query.filter(Trip.platform_id == platform_id)

    if status is not None:
        query = query.filter(Trip.status == status)

    return query.order_by(Trip.requested_at.desc()).all()


def update_trip(
    db: Session,
    trip_id: int,
    trip_data: TripUpdate,
) -> Trip | None:
    trip = db.get(Trip, trip_id)

    if trip is None:
        return None

    data = trip_data.model_dump(exclude_unset=True)

    pickup_lat = data.pop("pickup_latitude", None)
    pickup_lon = data.pop("pickup_longitude", None)
    dropoff_lat = data.pop("dropoff_latitude", None)
    dropoff_lon = data.pop("dropoff_longitude", None)

    if ("pickup_latitude" in trip_data.model_fields_set) != (
        "pickup_longitude" in trip_data.model_fields_set
    ):
        raise ValueError("Informe latitude e longitude da origem juntas.")

    if ("dropoff_latitude" in trip_data.model_fields_set) != (
        "dropoff_longitude" in trip_data.model_fields_set
    ):
        raise ValueError("Informe latitude e longitude do destino juntas.")

    if "vehicle_id" in data and data["vehicle_id"] is not None:
        vehicle = db.get(Vehicle, data["vehicle_id"])

        if vehicle is None or vehicle.driver_id != trip.driver_id:
            raise ValueError("Veículo não encontrado para este motorista.")

    if "pickup_latitude" in trip_data.model_fields_set:
        if pickup_lat is None:
            data["pickup_location"] = None
        else:
            data["pickup_location"] = WKTElement(
                f"POINT({pickup_lon} {pickup_lat})",
                srid=4326,
            )

    if "dropoff_latitude" in trip_data.model_fields_set:
        if dropoff_lat is None:
            data["dropoff_location"] = None
        else:
            data["dropoff_location"] = WKTElement(
                f"POINT({dropoff_lon} {dropoff_lat})",
                srid=4326,
            )

    for field, value in data.items():
        setattr(trip, field, value)

    db.commit()
    db.refresh(trip)

    return trip
