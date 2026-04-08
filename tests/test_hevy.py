import pytest
from unittest.mock import patch, MagicMock
from hevy import Set, Exercise, Workout, _parse_set, _parse_exercise, _parse_workout, get_workouts_since


SET_NORMAL = {
    "index": 0, "type": "normal", "weight_kg": 100.0, "reps": 10,
    "distance_meters": None, "duration_seconds": None, "rpe": None, "custom_metric": None,
}
SET_WARMUP = {
    "index": 1, "type": "warmup", "weight_kg": 40.0, "reps": 6,
    "distance_meters": None, "duration_seconds": None, "rpe": None, "custom_metric": None,
}
SET_CARDIO = {
    "index": 0, "type": "normal", "weight_kg": None, "reps": None,
    "distance_meters": 5000.0, "duration_seconds": 1800.0, "rpe": None, "custom_metric": None,
}
EXERCISE_DATA = {
    "index": 0, "title": "Bench Press (Barbell)", "notes": "",
    "exercise_template_id": "ABC", "superset_id": None,
    "sets": [SET_NORMAL, SET_WARMUP],
}
WORKOUT_DATA = {
    "id": "abc-123", "title": "Push Day", "description": "", "routine_id": "r1",
    "start_time": "2026-04-07T10:00:00+00:00", "end_time": "2026-04-07T11:30:00+00:00",
    "updated_at": "2026-04-07T11:30:00+00:00", "created_at": "2026-04-07T11:30:00+00:00",
    "exercises": [EXERCISE_DATA],
}


def test_parse_set_normal():
    s = _parse_set(SET_NORMAL)
    assert s.index == 0
    assert s.type == "normal"
    assert s.weight_kg == 100.0
    assert s.reps == 10
    assert s.distance_meters is None
    assert s.duration_seconds is None


def test_parse_set_cardio():
    s = _parse_set(SET_CARDIO)
    assert s.weight_kg is None
    assert s.reps is None
    assert s.distance_meters == 5000.0
    assert s.duration_seconds == 1800.0


def test_parse_exercise():
    e = _parse_exercise(EXERCISE_DATA)
    assert e.title == "Bench Press (Barbell)"
    assert len(e.sets) == 2
    assert e.sets[0].type == "normal"
    assert e.sets[1].type == "warmup"


def test_parse_workout():
    w = _parse_workout(WORKOUT_DATA)
    assert w.id == "abc-123"
    assert w.title == "Push Day"
    assert w.start_time == "2026-04-07T10:00:00+00:00"
    assert w.end_time == "2026-04-07T11:30:00+00:00"
    assert len(w.exercises) == 1


def _api_response(workouts, page=1, page_count=1):
    return {"page": page, "page_count": page_count, "workouts": workouts}


def _stub(id, start_time, title="Workout"):
    return {
        "id": id, "title": title, "description": "", "routine_id": None,
        "start_time": start_time, "end_time": start_time,
        "updated_at": start_time, "created_at": start_time, "exercises": [],
    }


@patch("hevy.requests.get")
def test_get_workouts_since_empty_since_returns_all(mock_get):
    mock_get.return_value.raise_for_status = MagicMock()
    mock_get.return_value.json.return_value = _api_response([
        _stub("w2", "2026-04-07T10:00:00+00:00"),
        _stub("w1", "2026-04-06T10:00:00+00:00"),
    ])
    result = get_workouts_since("key", "")
    assert len(result) == 2


@patch("hevy.requests.get")
def test_get_workouts_since_filters_old(mock_get):
    mock_get.return_value.raise_for_status = MagicMock()
    mock_get.return_value.json.return_value = _api_response([
        _stub("w2", "2026-04-07T10:00:00+00:00"),
        _stub("w1", "2026-04-04T10:00:00+00:00"),
    ])
    result = get_workouts_since("key", "2026-04-05T00:00:00+00:00")
    assert len(result) == 1
    assert result[0].id == "w2"


@patch("hevy.requests.get")
def test_get_workouts_since_sorted_oldest_first(mock_get):
    mock_get.return_value.raise_for_status = MagicMock()
    mock_get.return_value.json.return_value = _api_response([
        _stub("w2", "2026-04-07T10:00:00+00:00"),
        _stub("w1", "2026-04-06T10:00:00+00:00"),
    ])
    result = get_workouts_since("key", "")
    assert result[0].id == "w1"
    assert result[1].id == "w2"


@patch("hevy.requests.get")
def test_get_workouts_since_paginates(mock_get):
    mock_get.return_value.raise_for_status = MagicMock()
    mock_get.return_value.json.side_effect = [
        _api_response([_stub("w2", "2026-04-07T10:00:00+00:00")], page=1, page_count=2),
        _api_response([_stub("w1", "2026-04-06T10:00:00+00:00")], page=2, page_count=2),
    ]
    result = get_workouts_since("key", "")
    assert len(result) == 2
    assert mock_get.call_count == 2


@patch("hevy.requests.get")
def test_get_workouts_since_stops_early_on_old_workout(mock_get):
    mock_get.return_value.raise_for_status = MagicMock()
    mock_get.return_value.json.return_value = _api_response(
        [
            _stub("w2", "2026-04-07T10:00:00+00:00"),
            _stub("w1", "2026-04-01T10:00:00+00:00"),
        ],
        page=1, page_count=5,
    )
    result = get_workouts_since("key", "2026-04-05T00:00:00+00:00")
    assert len(result) == 1
    assert result[0].id == "w2"
    assert mock_get.call_count == 1
