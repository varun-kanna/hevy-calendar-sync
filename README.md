# hevy-calendar-sync

Syncs Hevy workouts to Google Calendar. Each workout becomes a calendar event with the exact start/end times recorded by Hevy.

## Requirements

- Python 3.11+
- A [Hevy Pro](https://www.hevyapp.com) subscription (required for API access)
- A Google account

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get your Hevy API key

Go to [hevy.com/settings?developer](https://www.hevyapp.com/settings?developer) and copy your API key.

### 3. Set up Google Calendar access (one-time, ~5 minutes)

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and sign in
2. Click **Select a project → New Project** → name it anything (e.g. "hevy-sync") → **Create**
3. In the search bar, type **Google Calendar API** → click the result → **Enable**
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**
5. If asked to configure the consent screen first: choose **External**, fill in an app name, click through the rest
6. For application type, choose **Desktop app** → name it anything → **Create**
7. Click **Download JSON** → save the file as `credentials.json` in this folder

### 4. Configure `config.toml`

```toml
[hevy]
api_key = "paste-your-hevy-api-key-here"

[google_calendar]
credentials_file = "credentials.json"
calendar_id = "primary"         # "primary" = your main calendar

[preferences]
description_format = "detailed" # "minimal" or "detailed"
weight_unit = "lbs"             # "kg" or "lbs"
```

## Usage

```bash
python sync.py
```

The first time you run it, a browser window will open asking you to grant access to your Google Calendar. After you approve, a `token.json` file is saved and you won't be prompted again.

Subsequent runs only fetch workouts logged since the last sync. Progress is tracked in `state.toml`.

## What the events look like

**Event title:** `Push Day · 12450.3 lbs`

**Detailed description:**
```
Incline Bench Press (Dumbbell)
  120.0 lbs × 9, 120.0 lbs × 9, 40.0 lbs × 5 (warmup)

Overhead Press (Barbell)
  75.0 lbs × 8, 75.0 lbs × 9
```

**Minimal description:**
```
Incline Bench Press (Dumbbell)
Overhead Press (Barbell)
Chest Press (Machine)
```

## Files

| File | What it is |
|---|---|
| `config.toml` | Your settings — edit this |
| `credentials.json` | Downloaded from Google Cloud — never committed |
| `state.toml` | Tracks last sync time — managed by the script |
| `token.json` | Google auth token — managed by the script |
