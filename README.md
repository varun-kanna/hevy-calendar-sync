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

Go to [hevy.com/settings?developer](https://www.hevyapp.com/settings?developer) after logging in and copy your API key.

### 3. Set up Google Calendar access (one-time)

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and sign in
2. Click **Select a project → New Project** → name it anything (e.g. "hevy-sync") → **Create**
3. In the search bar, type **Google Calendar API** → click the result → **Enable**
4. Go to **APIs & Services → OAuth consent screen**
5. Click **Get started**
6. Fill in an app name (anything) and your email for the support contact field → **Next**
7. Under **Audience**, select **External** → **Next**
8. Enter your email for the developer contact field → **Next**
9. Agree to the terms → **Create**
10. In the left sidebar click **Audience**, scroll to **Test users** → **Add users**, enter your Google account email → **Save**
11. In the left sidebar click **Clients** → **Create client**
12. For application type choose **Desktop app** → name it anything → **Create**
13. Click **Download JSON** → save the file as `credentials.json` in this folder

### 4. Configure `config.toml`

```toml
[hevy]
api_key = "paste-your-hevy-api-key-here"

[google_calendar]
credentials_file = "credentials.json"
calendar_id = "primary"         # see below

[preferences]
description_format = "detailed" # "minimal" or "detailed"
weight_unit = "lbs"             # "kg" or "lbs"
```

**Finding your `calendar_id`:** Use `"primary"` for your main Google Calendar. For any other calendar, open [calendar.google.com](https://calendar.google.com), click the three dots next to the calendar name → **Settings and sharing** → scroll to **Integrate calendar** → copy the **Calendar ID** (it looks like `abc123...@group.calendar.google.com`).

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
