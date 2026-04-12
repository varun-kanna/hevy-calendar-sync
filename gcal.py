import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from hevy import Workout
from config import Config, State

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
KG_TO_LBS = 2.20462


def _kg_to_unit(kg: float, unit: str) -> float:
    return kg * KG_TO_LBS if unit == "lbs" else kg


def _calculate_volume(workout: Workout, unit: str) -> float:
    total = 0.0
    for exercise in workout.exercises:
        for s in exercise.sets:
            if s.weight_kg is not None and s.reps is not None:
                total += s.weight_kg * s.reps
    return round(_kg_to_unit(total, unit), 1)


def _format_minimal(workout: Workout) -> str:
    return "\n".join(e.title for e in workout.exercises)


def _format_detailed(workout: Workout, unit: str) -> str:
    blocks = []
    for exercise in workout.exercises:
        parts = []
        for s in exercise.sets:
            if s.weight_kg is not None and s.reps is not None:
                weight = round(_kg_to_unit(s.weight_kg, unit), 1)
                label = f"{weight} {unit} × {s.reps}"
            elif s.duration_seconds is not None:
                label = f"{int(s.duration_seconds)}s"
            elif s.distance_meters is not None:
                label = f"{s.distance_meters}m"
            else:
                continue
            if s.type == "warmup":
                label += " (warmup)"
            parts.append(label)
        set_line = "  " + ", ".join(parts) if parts else ""
        blocks.append(exercise.title + ("\n" + set_line if set_line else ""))
    return "\n\n".join(blocks)


def _build_description(workout: Workout, config: Config) -> str:
    if config.preferences.description_format == "minimal":
        return _format_minimal(workout)
    return _format_detailed(workout, config.preferences.weight_unit)


def _build_summary(workout: Workout, config: Config) -> str:
    volume = _calculate_volume(workout, config.preferences.weight_unit)
    return f"{workout.title} · {volume} {config.preferences.weight_unit}"


def build_service(config: Config, state: State):
    creds = None
    token_path = state.token_file

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.google_calendar.credentials_file, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def validate_calendar(service, calendar_id: str) -> None:
    try:
        service.events().list(calendarId=calendar_id, maxResults=1).execute()
    except HttpError as e:
        if e.status_code == 404:
            raise SystemExit(
                f"Error: Calendar '{calendar_id}' not found. "
                "Check [google_calendar] calendar_id in config.toml."
            )
        raise


def find_event_id(service, calendar_id: str, workout_id: str) -> str | None:
    result = service.events().list(
        calendarId=calendar_id,
        privateExtendedProperty=f"hevy_workout_id={workout_id}",
    ).execute()
    items = result.get("items", [])
    if not items:
        return None
    return items[0]["id"]


def sync_workout(service, workout: Workout, config: Config, event_id: str | None = None) -> str:
    event = {
        "summary": _build_summary(workout, config),
        "description": _build_description(workout, config),
        "start": {"dateTime": workout.start_time},
        "end": {"dateTime": workout.end_time},
        "extendedProperties": {
            "private": {"hevy_workout_id": workout.id}
        },
    }
    if event_id:
        updated = service.events().update(
            calendarId=config.google_calendar.calendar_id,
            eventId=event_id,
            body=event,
        ).execute()
        return updated["id"]

    created = service.events().insert(
        calendarId=config.google_calendar.calendar_id,
        body=event,
    ).execute()
    return created["id"]
