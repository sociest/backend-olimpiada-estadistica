from datetime import datetime, timezone
from typing import Annotated, Union
from pydantic import BeforeValidator, PlainSerializer

def _validate_utc_datetime(v: Union[str, datetime]) -> datetime:
    if isinstance(v, str):
        v = datetime.fromisoformat(v)
    if v.tzinfo is None:
        # Asumimos UTC si no tiene zona horaria (o podés lanzar error)
        v = v.replace(tzinfo=timezone.utc)
    return v.astimezone(timezone.utc)

def _serialize_utc_datetime(v: datetime) -> str:
    if v.tzinfo is None:
        v = v.replace(tzinfo=timezone.utc)
    return v.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

UTCDateTimeInput = Annotated[
    datetime,
    BeforeValidator(_validate_utc_datetime),
]

UTCDateTimeOutput = Annotated[
    datetime,
    BeforeValidator(_validate_utc_datetime),
    PlainSerializer(_serialize_utc_datetime, return_type=str),
]