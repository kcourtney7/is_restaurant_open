import csv
import re
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from functools import lru_cache
from pathlib import Path

from django.http import JsonResponse
from django.views.decorators.http import require_GET


DAY_INDEX = {
    "mon": 0,
    "monday": 0,
    "tue": 1,
    "tues": 1,
    "tuesday": 1,
    "wed": 2,
    "weds": 2,
    "wednesday": 2,
    "thu": 3,
    "thur": 3,
    "thurs": 3,
    "thursday": 3,
    "fri": 4,
    "friday": 4,
    "sat": 5,
    "saturday": 5,
    "sun": 6,
    "sunday": 6,
}
TIME_RE = re.compile(r"(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?\s*(?P<ampm>am|pm)", re.IGNORECASE)


@dataclass(frozen=True)
class ScheduleEntry:
    day_index: int
    open_time: time
    close_time: time


@lru_cache(maxsize=1)
def load_restaurants():
    csv_path = Path(__file__).resolve().with_name("restaurants.csv")
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return tuple(
            {
                "name": row["Restaurant Name"],
                "hours": row["Hours"],
            }
            for row in reader
        )


def parse_datetime(value):
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError("datetime string is required")
        if text.endswith("Z") or text.endswith("z"):
            text = text[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]:
                try:
                    parsed = datetime.strptime(text, fmt)
                    break
                except ValueError:
                    parsed = None
            if parsed is None:
                raise ValueError(f"Unrecognized datetime format: {value}")
    else:
        raise TypeError("timestamp must be a datetime or string")

    if parsed.tzinfo is not None:
        parsed = parsed.replace(tzinfo=None)
    return parsed


def normalize_day_token(token):
    cleaned = token.strip().replace(".", "").lower()
    if cleaned not in DAY_INDEX:
        raise ValueError(f"Unsupported day token: {token}")
    return DAY_INDEX[cleaned]


def open_after_midnight(start_token, end_token):
    start_day = normalize_day_token(start_token)
    end_day = normalize_day_token(end_token)
    if start_day <= end_day:
        return list(range(start_day, end_day + 1))
    return list(range(start_day, 7)) + list(range(0, end_day + 1))


def parse_time_segment(value):
    value = value.strip().lower()
    match = TIME_RE.search(value)
    if not match:
        raise ValueError(f"Unsupported time value: {value}")
    hour = int(match.group("hour"))
    minute = int(match.group("minute") or 0)
    ampm = match.group("ampm").lower()
    if ampm == "pm" and hour != 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0
    return time(hour, minute)


def parse_hours(hours):
    entries = []
    for segment in hours.split("/"):
        segment = segment.strip()
        if not segment:
            continue

        time_match = re.search(r"\d", segment)
        if not time_match:
            continue

        days_part = segment[:time_match.start()].strip()
        times_part = segment[time_match.start():].strip()

        if not days_part or not times_part:
            continue

        open_part, close_part = [part.strip() for part in re.split(r"\s*-\s*", times_part, maxsplit=1)]
        if len([part for part in [open_part, close_part] if part]) != 2:
            raise ValueError(f"Could not parse hours: {hours}")

        open_time = parse_time_segment(open_part)
        close_time = parse_time_segment(close_part)

        day_tokens = [token.strip() for token in days_part.split(",") if token.strip()]
        for token in day_tokens:
            if "-" in token:
                start_token, end_token = [piece.strip() for piece in token.split("-", 1)]
                day_indices = open_after_midnight(start_token, end_token)
            else:
                day_indices = [normalize_day_token(token)]
            for day_index in day_indices:
                entries.append(ScheduleEntry(day_index=day_index, open_time=open_time, close_time=close_time))
    return entries


def is_restaurant_open(hours, timestamp):
    timestamp = parse_datetime(timestamp)
    current_day = timestamp.weekday()

    for entry in parse_hours(hours):
        start_date = timestamp.date() - timedelta(days=(current_day - entry.day_index) % 7)
        start_datetime = datetime.combine(start_date, entry.open_time)
        end_datetime = datetime.combine(start_date, entry.close_time)
        if entry.close_time <= entry.open_time:
            end_datetime += timedelta(days=1)
        if start_datetime <= timestamp < end_datetime:
            return True
    return False


def get_open_restaurants(timestamp):
    dt = parse_datetime(timestamp)
    open_restaurants = []
    for restaurant in load_restaurants():
        if is_restaurant_open(restaurant["hours"], dt):
            open_restaurants.append(restaurant["name"])
    return open_restaurants


@require_GET
def restaurants_open(request):
    timestamp = request.GET.get("datetime")
    if not timestamp:
        return JsonResponse({"error": "datetime query parameter is required"}, status=400)

    try:
        restaurants = get_open_restaurants(timestamp)
    except (TypeError, ValueError) as exc:
        return JsonResponse({"error": str(exc)}, status=400)

    return JsonResponse({"datetime": timestamp, "restaurants": restaurants})
