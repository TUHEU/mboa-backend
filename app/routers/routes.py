from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.schemas.route import RouteRequest, RouteResponse
from app.services.map_service import (
    RoutesConfigurationError,
    RoutesProviderError,
    compute_google_route,
)


router = APIRouter(
    prefix="/routes",
    tags=["Routes"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/compute", response_model=RouteResponse)
def compute_route(payload: RouteRequest) -> RouteResponse:
    waypoints = [
        (point.latitude, point.longitude) for point in payload.waypoints
    ]
    try:
        route = compute_google_route(
            waypoints,
            get_settings().google_routes_api_key,
        )
    except RoutesConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google Routes is not configured.",
        ) from error
    except RoutesProviderError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google Routes could not calculate this itinerary.",
        ) from error
    return RouteResponse.model_validate(route)