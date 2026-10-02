from fastapi.testclient import TestClient

TWO_STOPS = {
    "waypoints": [
        {"latitude": 3.86, "longitude": 11.51},
        {"latitude": 3.90, "longitude": 11.55},
    ]
}


def test_compute_route_returns_google_route(
    client: TestClient, auth_headers, monkeypatch
):
    monkeypatch.setattr(
        "app.routers.routes.compute_google_route",
        lambda waypoints, api_key: {
            "distance_meters": 12500,
            "duration_seconds": 1800,
            "encoded_polyline": "encoded-route",
        },
    )

    response = client.post(
        "/api/v1/routes/compute", json=TWO_STOPS, headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["distance_meters"] == 12500
    assert response.json()["duration_seconds"] == 1800
    assert response.json()["encoded_polyline"] == "encoded-route"


def test_compute_route_requires_authentication(client: TestClient):
    response = client.post("/api/v1/routes/compute", json=TWO_STOPS)
    assert response.status_code == 401

    response = client.post(
        "/api/v1/routes/compute",
        json=TWO_STOPS,
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert response.status_code == 401


def test_compute_route_validates_waypoint_count(
    client: TestClient, auth_headers
):
    response = client.post(
        "/api/v1/routes/compute",
        json={"waypoints": [{"latitude": 3.86, "longitude": 11.51}]},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_compute_route_reports_missing_configuration(
    client: TestClient, auth_headers
):
    response = client.post(
        "/api/v1/routes/compute", json=TWO_STOPS, headers=auth_headers
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "Google Routes is not configured."
