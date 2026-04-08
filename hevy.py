from dataclasses import dataclass
import requests


@dataclass
class Set:
    index: int
    type: str
    weight_kg: float | None
    reps: int | None
    distance_meters: float | None
    duration_seconds: float | None


@dataclass
class Exercise:
    index: int
    title: str
    notes: str
    sets: list[Set]


@dataclass
class Workout:
    id: str
    title: str
    description: str
    start_time: str
    end_time: str
    exercises: list[Exercise]


BASE_URL = "https://api.hevyapp.com"


def _parse_set(data: dict) -> Set:
    return Set(
        index=data["index"],
        type=data["type"],
        weight_kg=data.get("weight_kg"),
        reps=data.get("reps"),
        distance_meters=data.get("distance_meters"),
        duration_seconds=data.get("duration_seconds"),
    )


def _parse_exercise(data: dict) -> Exercise:
    return Exercise(
        index=data["index"],
        title=data["title"],
        notes=data.get("notes", ""),
        sets=[_parse_set(s) for s in data.get("sets", [])],
    )


def _parse_workout(data: dict) -> Workout:
    return Workout(
        id=data["id"],
        title=data["title"],
        description=data.get("description", ""),
        start_time=data["start_time"],
        end_time=data["end_time"],
        exercises=[_parse_exercise(e) for e in data.get("exercises", [])],
    )


def get_workouts_since(api_key: str, since: str) -> list[Workout]:
    """
    Fetch all workouts with start_time > since (or all if since is empty).
    Returns workouts sorted oldest → newest.
    """
    headers = {"api-key": api_key}
    collected = []
    page = 1

    while True:
        response = requests.get(
            f"{BASE_URL}/v1/workouts",
            headers=headers,
            params={"page": page, "pageSize": 10},
        )
        response.raise_for_status()
        data = response.json()

        page_workouts = data.get("workouts", [])
        page_count = data.get("page_count", 1)

        done = False
        for w in page_workouts:
            if since and w["start_time"] <= since:
                done = True
                break
            collected.append(_parse_workout(w))

        if done or page >= page_count:
            break
        page += 1

    return sorted(collected, key=lambda w: w.start_time)
