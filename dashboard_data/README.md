# dashboard_data/ — Home Screen Card Data

Each JSON file in this folder powers one card on the MCC Home screen.

## How to add a new card

Create a JSON file in this folder with these fields:

```json
{
  "tab_name": "My Feature",
  "tab_id": "my-tab",
  "icon": "🔧",
  "status": "green",
  "facts": [
    "First key fact here",
    "Second key fact here",
    "Third key fact (optional)"
  ],
  "last_updated": "2026-05-23T12:00:00"
}
```

The home screen will pick it up automatically on the next 30-second refresh.

## Fields

| Field        | Required | Description                                                |
|--------------|----------|------------------------------------------------------------|
| tab_name     | Yes      | Card title shown on the home screen                        |
| tab_id       | Yes      | Matching `data-tab` value in the tab bar (for navigation)  |
| icon         | Yes      | Emoji shown in the card header                             |
| status       | Yes      | `green`, `yellow`, or `red` — drives the coloured dot      |
| facts        | Yes      | Array of 1–3 short fact strings to display                 |
| last_updated | No       | ISO timestamp — shown as small footer in the card          |

## Status meanings

- **green** — data is fresh and healthy
- **yellow** — data exists but may be stale or partial
- **red** — no data, error, or service down

## How it works

1. The MCC home screen calls `GET /dashboard-data/` every 30 seconds.
2. The server returns a list of all `.json` files in this folder.
3. The home screen fetches each file and renders one card per file.
4. Clicking a card navigates to the tab whose `data-tab` matches `tab_id`.
5. If the tab does not exist yet, a toast message is shown instead.
