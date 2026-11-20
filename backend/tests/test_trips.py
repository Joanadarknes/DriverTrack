import pytest

from backend.app.models.driver import Driver
from backend.app.models.platform import Platform


@pytest.fixture
def trip_context(db_session):
    driver = Driver(
        full_name="Motorista Teste",
        email="teste@drivertrack.local",
        phone="11999999999",
    )

    platform = Platform(
        name="Uber Teste",
        code="test-uber",
        color="#FFFFFF",
    )

    db_session.add_all([driver, platform])
    db_session.commit()

    db_session.refresh(driver)
    db_session.refresh(platform)

    return {
        "driver_id": driver.id,
        "platform_id": platform.id,
    }


def test_create_trip_and_record_gps(client, trip_context):
    trip_response = client.post(
        "/api/v1/trips",
        json={
            "driver_id": trip_context["driver_id"],
            "platform_id": trip_context["platform_id"],
            "pickup_address": "Avenida Paulista, São Paulo",
            "dropoff_address": "Rua Augusta, São Paulo",
            "pickup_latitude": -23.5614,
            "pickup_longitude": -46.6559,
            "dropoff_latitude": -23.5537,
            "dropoff_longitude": -46.6588,
            "pickup_distance_km": 2.4,
            "trip_distance_km": 8.6,
            "fare_amount": 32.50,
            "status": "in_progress",
        },
    )

    assert trip_response.status_code == 201

    trip = trip_response.json()
    trip_id = trip["id"]

    assert trip["driver_id"] == trip_context["driver_id"]
    assert trip["platform_id"] == trip_context["platform_id"]

    gps_response = client.post(
        f"/api/v1/trips/{trip_id}/locations",
        json={
            "latitude": -23.5550,
            "longitude": -46.6560,
            "speed_kmh": 30,
            "accuracy_m": 5,
            "heading_degrees": 135,
        },
    )

    assert gps_response.status_code == 201

    gps = gps_response.json()

    assert gps["trip_id"] == trip_id
    assert gps["latitude"] == pytest.approx(-23.5550)
    assert gps["longitude"] == pytest.approx(-46.6560)

    locations_response = client.get(
        f"/api/v1/trips/{trip_id}/locations"
    )

    assert locations_response.status_code == 200

    locations = locations_response.json()

    assert len(locations) == 1
    assert locations[0]["latitude"] == pytest.approx(-23.5550)
    assert locations[0]["longitude"] == pytest.approx(-46.6560)


def test_get_nonexistent_trip_returns_404(client):
    response = client.get("/api/v1/trips/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Corrida não encontrada."


def test_record_location_for_nonexistent_trip_returns_404(client):
    response = client.post(
        "/api/v1/trips/999999/locations",
        json={
            "latitude": -23.5550,
            "longitude": -46.6560,
            "speed_kmh": 30,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Corrida não encontrada."

def test_update_trip_status(client, trip_context):
    create_response = client.post(
        "/api/v1/trips",
        json={
            "driver_id": trip_context["driver_id"],
            "platform_id": trip_context["platform_id"],
            "pickup_address": "Avenida Paulista",
            "dropoff_address": "Rua Augusta",
            "fare_amount": 32.50,
            "status": "requested",
        },
    )

    assert create_response.status_code == 201

    trip_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/trips/{trip_id}",
        json={
            "status": "in_progress",
            "started_at": "2026-11-20T03:00:00Z",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "in_progress"
    assert update_response.json()["started_at"] is not None


def test_financial_summary(client, trip_context):
    create_response = client.post(
        "/api/v1/trips",
        json={
            "driver_id": trip_context["driver_id"],
            "platform_id": trip_context["platform_id"],
            "pickup_distance_km": 2.4,
            "trip_distance_km": 8.6,
            "fare_amount": 32.50,
            "tip_amount": 2.50,
            "platform_fee_amount": 5.00,
            "tolls_amount": 2.00,
            "parking_amount": 1.00,
            "fuel_cost_amount": 4.20,
            "other_expenses_amount": 0.80,
            "status": "completed",
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        "/api/v1/trips/summary",
        params={"driver_id": trip_context["driver_id"]},
    )

    assert response.status_code == 200

    summary = response.json()

    assert summary["completed_trips"] == 1
    assert float(summary["gross_revenue"]) == pytest.approx(35.00)
    assert float(summary["total_expenses"]) == pytest.approx(13.00)
    assert float(summary["net_profit"]) == pytest.approx(22.00)
    assert float(summary["total_distance_km"]) == pytest.approx(11.00)


def test_financial_summary_date_filter(client, trip_context):
    client.post(
        "/api/v1/trips",
        json={
            "driver_id": trip_context["driver_id"],
            "platform_id": trip_context["platform_id"],
            "fare_amount": 100.00,
            "fuel_cost_amount": 20.00,
            "pickup_distance_km": 2,
            "trip_distance_km": 8,
            "status": "completed",
            "completed_at": "2026-11-20T15:00:00Z",
        },
    )

    response = client.get(
        "/api/v1/trips/summary",
        params={
            "driver_id": trip_context["driver_id"],
            "start_date": "2026-11-20",
            "end_date": "2026-11-20",
        },
    )

    assert response.status_code == 200

    summary = response.json()

    assert summary["completed_trips"] == 1
    assert float(summary["gross_revenue"]) == 100.00
    assert float(summary["net_profit"]) == 80.00


def test_financial_summary_invalid_date_range(client, trip_context):
    response = client.get(
        "/api/v1/trips/summary",
        params={
            "driver_id": trip_context["driver_id"],
            "start_date": "2026-11-25",
            "end_date": "2026-11-20",
        },
    )

    assert response.status_code == 422


def test_financial_summary_by_platform_returns_official_platforms(
    client,
    trip_context,
):
    response = client.get(
        "/api/v1/trips/summary/by-platform",
        params={"driver_id": trip_context["driver_id"]},
    )

    assert response.status_code == 200

    summaries = response.json()

    platforms = {
        item["platform_code"]: item
        for item in summaries
    }

    assert "uber" in platforms
    assert "99" in platforms
    assert "indrive" in platforms

    assert platforms["uber"]["platform_name"] == "Uber"
    assert platforms["uber"]["platform_color"] == "#FFFFFF"

    assert platforms["99"]["platform_name"] == "99"
    assert platforms["99"]["platform_color"] == "#FFD500"

    assert platforms["indrive"]["platform_name"] == "inDrive"
    assert platforms["indrive"]["platform_color"] == "#20C978"

    for code in ("uber", "99", "indrive"):
        assert platforms[code]["completed_trips"] == 0
        assert platforms[code]["gross_revenue"] == "0.00"
        assert platforms[code]["total_expenses"] == "0.00"
        assert platforms[code]["net_profit"] == "0.00"


def test_financial_summary_by_platform_rounds_values_and_counts_tolls(
    client,
    db_session,
    trip_context,
):
    uber = (
        db_session.query(Platform)
        .filter(Platform.code == "uber")
        .first()
    )

    assert uber is not None

    trip_response = client.post(
        "/api/v1/trips",
        json={
            "driver_id": trip_context["driver_id"],
            "platform_id": uber.id,
            "pickup_distance_km": 2,
            "trip_distance_km": 20,
            "fare_amount": 65,
            "tolls_amount": 8.40,
            "status": "completed",
        },
    )

    assert trip_response.status_code == 201

    response = client.get(
        "/api/v1/trips/summary/by-platform",
        params={"driver_id": trip_context["driver_id"]},
    )

    assert response.status_code == 200

    uber_summary = next(
        item
        for item in response.json()
        if item["platform_code"] == "uber"
    )

    assert uber_summary["completed_trips"] == 1
    assert uber_summary["gross_revenue"] == "65.00"
    assert uber_summary["total_expenses"] == "8.40"
    assert uber_summary["net_profit"] == "56.60"
    assert uber_summary["total_distance_km"] == "22.00"
    assert uber_summary["revenue_per_km"] == "2.95"
    assert uber_summary["profit_per_km"] == "2.57"
    assert uber_summary["average_revenue_per_trip"] == "65.00"


def test_financial_summary_by_platform_respects_date_filter(
    client,
    db_session,
    trip_context,
):
    uber = (
        db_session.query(Platform)
        .filter(Platform.code == "uber")
        .first()
    )

    assert uber is not None

    trip_response = client.post(
        "/api/v1/trips",
        json={
            "driver_id": trip_context["driver_id"],
            "platform_id": uber.id,
            "fare_amount": 100,
            "fuel_cost_amount": 20,
            "pickup_distance_km": 2,
            "trip_distance_km": 8,
            "status": "completed",
            "completed_at": "2026-11-20T15:00:00Z",
        },
    )

    assert trip_response.status_code == 201

    inside_period = client.get(
        "/api/v1/trips/summary/by-platform",
        params={
            "driver_id": trip_context["driver_id"],
            "start_date": "2026-11-20",
            "end_date": "2026-11-20",
        },
    )

    assert inside_period.status_code == 200

    uber_summary = next(
        item for item in inside_period.json()
        if item["platform_code"] == "uber"
    )

    assert uber_summary["completed_trips"] == 1
    assert uber_summary["gross_revenue"] == "100.00"
    assert uber_summary["net_profit"] == "80.00"

    outside_period = client.get(
        "/api/v1/trips/summary/by-platform",
        params={
            "driver_id": trip_context["driver_id"],
            "start_date": "2026-11-21",
            "end_date": "2026-11-21",
        },
    )

    assert outside_period.status_code == 200

    uber_outside = next(
        item for item in outside_period.json()
        if item["platform_code"] == "uber"
    )

    assert uber_outside["completed_trips"] == 0
    assert uber_outside["gross_revenue"] == "0.00"


def test_financial_summary_by_platform_rejects_invalid_date_range(
    client,
    trip_context,
):
    response = client.get(
        "/api/v1/trips/summary/by-platform",
        params={
            "driver_id": trip_context["driver_id"],
            "start_date": "2026-11-25",
            "end_date": "2026-11-20",
        },
    )

    assert response.status_code == 422
