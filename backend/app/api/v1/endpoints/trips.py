from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.financial import (
    FinancialSummary,
    PlatformFinancialSummary,
)
from backend.app.schemas.trip import (
    TripCreate,
    TripRead,
    TripUpdate,
    TripStatus,
)
from backend.app.schemas.trip_location import (
    TripLocationCreate,
    TripLocationRead,
)
from backend.app.services.financial_service import (
    get_financial_summary,
    get_financial_summary_by_platform,
)
from backend.app.services.trip_service import (
    create_trip,
    get_trip,
    list_trips,
    update_trip,
)
from backend.app.services.trip_location_service import (
    record_trip_location,
    list_trip_locations,
)


router = APIRouter(prefix="/trips", tags=["Corridas"])


def validate_date_range(
    start_date: date | None,
    end_date: date | None,
):
    if (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    ):
        raise HTTPException(
            status_code=422,
            detail="A data inicial não pode ser posterior à data final.",
        )


@router.post("", response_model=TripRead, status_code=201)
def create_trip_endpoint(
    trip_data: TripCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_trip(db, trip_data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("", response_model=list[TripRead])
def list_trips_endpoint(
    driver_id: int = Query(gt=0),
    platform_id: int | None = Query(default=None, gt=0),
    status: TripStatus | None = None,
    db: Session = Depends(get_db),
):
    return list_trips(
        db=db,
        driver_id=driver_id,
        platform_id=platform_id,
        status=status,
    )


@router.get("/summary", response_model=FinancialSummary)
def financial_summary_endpoint(
    driver_id: int = Query(gt=0),
    platform_id: int | None = Query(default=None, gt=0),
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    validate_date_range(start_date, end_date)

    try:
        return get_financial_summary(
            db=db,
            driver_id=driver_id,
            platform_id=platform_id,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get(
    "/summary/by-platform",
    response_model=list[PlatformFinancialSummary],
)
def financial_summary_by_platform_endpoint(
    driver_id: int = Query(gt=0),
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
):
    validate_date_range(start_date, end_date)

    try:
        return get_financial_summary_by_platform(
            db=db,
            driver_id=driver_id,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/{trip_id}", response_model=TripRead)
def get_trip_endpoint(
    trip_id: int,
    db: Session = Depends(get_db),
):
    trip = get_trip(db, trip_id)

    if trip is None:
        raise HTTPException(
            status_code=404,
            detail="Corrida não encontrada.",
        )

    return trip


@router.patch("/{trip_id}", response_model=TripRead)
def update_trip_endpoint(
    trip_id: int,
    trip_data: TripUpdate,
    db: Session = Depends(get_db),
):
    try:
        trip = update_trip(db, trip_id, trip_data)

        if trip is None:
            raise HTTPException(
                status_code=404,
                detail="Corrida não encontrada.",
            )

        return trip

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post(
    "/{trip_id}/locations",
    response_model=TripLocationRead,
    status_code=201,
)
def record_trip_location_endpoint(
    trip_id: int,
    location_data: TripLocationCreate,
    db: Session = Depends(get_db),
):
    try:
        return record_trip_location(db, trip_id, location_data)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get(
    "/{trip_id}/locations",
    response_model=list[TripLocationRead],
)
def list_trip_locations_endpoint(
    trip_id: int,
    db: Session = Depends(get_db),
):
    trip = get_trip(db, trip_id)

    if trip is None:
        raise HTTPException(
            status_code=404,
            detail="Corrida não encontrada.",
        )

    return list_trip_locations(db, trip_id)
