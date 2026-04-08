import sys
from config import load_config, load_state, save_state, State
from hevy import get_workouts_since
from gcal import build_service, validate_calendar, event_exists, sync_workout


def main():
    config = load_config()
    state = load_state()

    print(f"Fetching workouts since: {state.last_synced_at or 'beginning of time'}")

    try:
        workouts = get_workouts_since(config.hevy.api_key, state.last_synced_at)
    except SystemExit:
        raise
    except Exception as e:
        print(f"Error fetching workouts from Hevy: {e}")
        sys.exit(1)

    if not workouts:
        print("No new workouts to sync.")
        return

    print(f"Found {len(workouts)} new workout(s) to sync.")

    service = build_service(config, state)
    validate_calendar(service, config.google_calendar.calendar_id)
    last_written_time = state.last_synced_at

    try:
        for workout in workouts:
            if event_exists(service, config.google_calendar.calendar_id, workout.id):
                print(f"  Skipping duplicate: {workout.title} ({workout.start_time[:10]})")
                last_written_time = workout.start_time
                continue
            sync_workout(service, workout, config)
            last_written_time = workout.start_time
            print(f"  Synced: {workout.title} ({workout.start_time[:10]})")
    finally:
        if last_written_time != state.last_synced_at:
            save_state(State(last_synced_at=last_written_time, token_file=state.token_file))
            print(f"State saved. Last synced: {last_written_time}")


if __name__ == "__main__":
    main()
