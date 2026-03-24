from datetime import datetime, UTC
from typing import Any


temp_session: dict[str, Any] = {
    "raw_user_query": None,
    "parsed_filters": None,
    "timestamp": None,
}


def save_raw_query(user_query: str) -> None:
    temp_session["raw_user_query"] = user_query
    temp_session["timestamp"] = datetime.now(UTC).isoformat()


def save_parsed_filters(filters_dict: dict) -> None:
    temp_session["parsed_filters"] = filters_dict


def get_session() -> dict[str, Any]:
    return temp_session