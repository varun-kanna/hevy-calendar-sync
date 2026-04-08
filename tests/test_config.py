import pytest
import tomli_w
from config import load_config, load_state, save_state, State


def write_toml(path, data):
    with open(path, "wb") as f:
        tomli_w.dump(data, f)


VALID = {
    "hevy": {"api_key": "test-key"},
    "google_calendar": {"credentials_file": "creds.json", "calendar_id": "primary"},
    "preferences": {"description_format": "detailed", "weight_unit": "lbs"},
}


def test_load_config_valid(tmp_path):
    p = tmp_path / "config.toml"
    write_toml(p, VALID)
    config = load_config(str(p))
    assert config.hevy.api_key == "test-key"
    assert config.google_calendar.credentials_file == "creds.json"
    assert config.google_calendar.calendar_id == "primary"
    assert config.preferences.description_format == "detailed"
    assert config.preferences.weight_unit == "lbs"


def test_load_config_missing_api_key(tmp_path):
    data = {**VALID, "hevy": {}}
    p = tmp_path / "config.toml"
    write_toml(p, data)
    with pytest.raises(SystemExit):
        load_config(str(p))


def test_load_config_missing_credentials_file(tmp_path):
    data = {**VALID, "google_calendar": {"calendar_id": "primary"}}
    p = tmp_path / "config.toml"
    write_toml(p, data)
    with pytest.raises(SystemExit):
        load_config(str(p))


def test_load_config_invalid_description_format(tmp_path):
    data = {**VALID, "preferences": {"description_format": "verbose", "weight_unit": "lbs"}}
    p = tmp_path / "config.toml"
    write_toml(p, data)
    with pytest.raises(SystemExit):
        load_config(str(p))


def test_load_config_invalid_weight_unit(tmp_path):
    data = {**VALID, "preferences": {"description_format": "minimal", "weight_unit": "stones"}}
    p = tmp_path / "config.toml"
    write_toml(p, data)
    with pytest.raises(SystemExit):
        load_config(str(p))


def test_load_state_missing_file(tmp_path):
    state = load_state(str(tmp_path / "nonexistent.toml"))
    assert state.last_synced_at == ""
    assert state.token_file == "token.json"


def test_load_state_existing_file(tmp_path):
    p = tmp_path / "state.toml"
    write_toml(p, {"last_synced_at": "2026-01-01T00:00:00+00:00", "token_file": "tok.json"})
    state = load_state(str(p))
    assert state.last_synced_at == "2026-01-01T00:00:00+00:00"
    assert state.token_file == "tok.json"


def test_save_state_roundtrip(tmp_path):
    p = tmp_path / "state.toml"
    original = State(last_synced_at="2026-04-08T10:00:00+00:00", token_file="tok.json")
    save_state(original, str(p))
    loaded = load_state(str(p))
    assert loaded.last_synced_at == original.last_synced_at
    assert loaded.token_file == original.token_file
