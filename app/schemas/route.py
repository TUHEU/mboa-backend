from pydantic import BaseModel, Field


class Coordinate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class RouteRequest(BaseModel):
    waypoints: list[Coordinate] = Field(min_length=2, max_length=25)


class RouteResponse(BaseModel):
    distance_meters: int
    duration_seconds: int
    encoded_polyline: str