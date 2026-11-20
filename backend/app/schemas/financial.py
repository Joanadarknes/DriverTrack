from decimal import Decimal

from pydantic import BaseModel


class FinancialSummary(BaseModel):
    driver_id: int
    platform_id: int | None

    completed_trips: int

    gross_revenue: Decimal
    total_expenses: Decimal
    net_profit: Decimal

    total_distance_km: Decimal
    revenue_per_km: Decimal
    profit_per_km: Decimal
    average_revenue_per_trip: Decimal


class PlatformFinancialSummary(FinancialSummary):
    platform_name: str
    platform_code: str
    platform_color: str
