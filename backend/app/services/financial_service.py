from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.models.driver import Driver
from backend.app.models.platform import Platform
from backend.app.models.trip import Trip
from backend.app.schemas.financial import (
    FinancialSummary,
    PlatformFinancialSummary,
)


ZERO = Decimal("0.00")
CENT = Decimal("0.01")


def round_money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def get_financial_summary(
    db: Session,
    driver_id: int,
    platform_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> FinancialSummary:

    driver = db.get(Driver, driver_id)

    if driver is None:
        raise ValueError("Motorista não encontrado.")

    query = db.query(Trip).filter(
        Trip.driver_id == driver_id,
        Trip.status == "completed",
    )

    if platform_id is not None:
        query = query.filter(Trip.platform_id == platform_id)

    if start_date is not None:
        query = query.filter(
            func.date(Trip.completed_at) >= start_date
        )

    if end_date is not None:
        query = query.filter(
            func.date(Trip.completed_at) <= end_date
        )

    trips = query.all()

    gross_revenue = ZERO
    total_expenses = ZERO
    total_distance = ZERO

    for trip in trips:
        gross_revenue += trip.fare_amount + trip.tip_amount

        total_expenses += (
            trip.platform_fee_amount
            + trip.tolls_amount
            + trip.parking_amount
            + trip.fuel_cost_amount
            + trip.other_expenses_amount
        )

        total_distance += (
            trip.pickup_distance_km + trip.trip_distance_km
        )

    net_profit = gross_revenue - total_expenses
    completed_trips = len(trips)

    revenue_per_km = (
        round_money(gross_revenue / total_distance)
        if total_distance > ZERO
        else ZERO
    )

    profit_per_km = (
        round_money(net_profit / total_distance)
        if total_distance > ZERO
        else ZERO
    )

    average_revenue_per_trip = (
        round_money(gross_revenue / completed_trips)
        if completed_trips > 0
        else ZERO
    )

    return FinancialSummary(
        driver_id=driver_id,
        platform_id=platform_id,
        completed_trips=completed_trips,
        gross_revenue=gross_revenue,
        total_expenses=total_expenses,
        net_profit=net_profit,
        total_distance_km=total_distance,
        revenue_per_km=revenue_per_km,
        profit_per_km=profit_per_km,
        average_revenue_per_trip=average_revenue_per_trip,
    )


def get_financial_summary_by_platform(
    db: Session,
    driver_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[PlatformFinancialSummary]:

    driver = db.get(Driver, driver_id)

    if driver is None:
        raise ValueError("Motorista não encontrado.")

    platforms = (
        db.query(Platform)
        .order_by(Platform.id.asc())
        .all()
    )

    summaries = []

    for platform in platforms:
        summary = get_financial_summary(
            db=db,
            driver_id=driver_id,
            platform_id=platform.id,
            start_date=start_date,
            end_date=end_date,
        )

        summaries.append(
            PlatformFinancialSummary(
                **summary.model_dump(),
                platform_name=platform.name,
                platform_code=platform.code,
                platform_color=platform.color,
            )
        )

    return summaries
