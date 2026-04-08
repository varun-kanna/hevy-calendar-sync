import sys
import tomllib
import tomli_w
from dataclasses import dataclass


@dataclass
class HevyConfig:
    api_key: str


@dataclass
class GoogleCalendarConfig:
    credentials_file: str
    calendar_id: str


@dataclass
class Preferences:
    description_format: str  # "minimal" or "detailed"
    weight_unit: str         # "kg" or "lbs"


@dataclass
class Config:
    hevy: HevyConfig
    google_calendar: GoogleCalendarConfig
    preferences: Preferences


@dataclass
class State:
    last_synced_at: str  # ISO 8601, or empty string on first run
    token_file: str


def load_config(path: str = "config.toml") -> Config:
    with open(path, "rb") as f:
        data = tomllib.load(f)

    required = {
        "[hevy] api_key": data.get("hevy", {}).get("api_key"),
        "[google_calendar] credentials_file": data.get("google_calendar", {}).get("credentials_file"),
        "[google_calendar] calendar_id": data.get("google_calendar", {}).get("calendar_id"),
        "[preferences] description_format": data.get("preferences", {}).get("description_format"),
        "[preferences] weight_unit": data.get("preferences", {}).get("weight_unit"),
    }
    for key, value in required.items():
        if not value:
            print(f"Error: Missing {key} in config.toml")
            sys.exit(1)

    pref = data["preferences"]
    if pref["description_format"] not in ("minimal", "detailed"):
        print("Error: [preferences] description_format must be 'minimal' or 'detailed'")
        sys.exit(1)
    if pref["weight_unit"] not in ("kg", "lbs"):
        print("Error: [preferences] weight_unit must be 'kg' or 'lbs'")
        sys.exit(1)

    return Config(
        hevy=HevyConfig(api_key=data["hevy"]["api_key"]),
        google_calendar=GoogleCalendarConfig(
            credentials_file=data["google_calendar"]["credentials_file"],
            calendar_id=data["google_calendar"]["calendar_id"],
        ),
        preferences=Preferences(
            description_format=pref["description_format"],
            weight_unit=pref["weight_unit"],
        ),
    )


def load_state(path: str = "state.toml") -> State:
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return State(
            last_synced_at=data.get("last_synced_at", ""),
            token_file=data.get("token_file", "token.json"),
        )
    except FileNotFoundError:
        return State(last_synced_at="", token_file="token.json")


def save_state(state: State, path: str = "state.toml") -> None:
    with open(path, "wb") as f:
        tomli_w.dump({"last_synced_at": state.last_synced_at, "token_file": state.token_file}, f)
