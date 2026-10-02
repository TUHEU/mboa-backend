import requests


class RoutesConfigurationError(Exception):
    pass


class RoutesProviderError(Exception):
    pass


def compute_google_route(
    waypoints: list[tuple[float, float]],
    api_key: str,
) -> dict[str, int | str]:
    if not api_key:
        raise RoutesConfigurationError

    def waypoint(point: tuple[float, float]) -> dict[str, object]:
        return {
            "location": {
                "latLng": {
                    "latitude": point[0],
                    "longitude": point[1],
                }
            }
        }

    response = requests.post(
        "https://routes.googleapis.com/directions/v2:computeRoutes",
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": (
                "routes.distanceMeters,routes.duration,"
                "routes.polyline.encodedPolyline"
            ),
        },
        json={
            "origin": waypoint(waypoints[0]),
            "destination": waypoint(waypoints[-1]),
            "intermediates": [waypoint(point) for point in waypoints[1:-1]],
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
            "computeAlternativeRoutes": False,
        },
        timeout=15,
    )
    if response.status_code != 200:
        raise RoutesProviderError
    routes = response.json().get("routes", [])
    if not routes:
        raise RoutesProviderError
    route = routes[0]
    duration = str(route["duration"]).removesuffix("s")
    return {
        "distance_meters": int(route["distanceMeters"]),
        "duration_seconds": round(float(duration)),
        "encoded_polyline": str(route["polyline"]["encodedPolyline"]),
    }