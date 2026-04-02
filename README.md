# Personal Calendar

A modern personal calendar repository that aggregates multiple sources into a single interactive schedule display.

## Features
- Interactive calendar powered by FullCalendar (dayGrid, timeGrid, list views)
- Extensible source integration through `calendar/sync_calendar.py`
- Event categories for visual distinctions
- Simple Quarto-based web deployment
- Unit tests with Python `unittest`

## Repository Structure
```
calendar/
├── index.qmd          # Quarto UI template with FullCalendar
├── _quarto.yml        # Quarto configuration
├── styles.css         # Optional styles
└── sync_calendar.py   # Event collection and JS generation

tests/
└── test_sync_calendar.py
```

## Usage
1. Configure calendar sources in `calendar/sync_calendar.py` by adding callable functions to `CALENDAR_SOURCES`.
2. Run synchronization:
   ```bash
   python calendar/sync_calendar.py
   ```
3. Render website:
   ```bash
   quarto render calendar
   ```
4. Open `calendar/_site/index.html` in a web browser.

## Event Source Example
In `calendar/sync_calendar.py`:
```python
CALENDAR_SOURCES = [
    lambda: [
        {
            "id": "evt1",
            "title": "Doctor appointment",
            "start": "2026-04-10T09:00:00",
            "end": "2026-04-10T10:00:00",
            "category": "personal",
            "description": "Annual checkup",
            "url": "https://example.com/appointment"
        },
    ]
]
```

## Development
- Run tests:
  ```bash
  python -m unittest discover tests/ -v
  ```
- Linting / formatting: add your preferred tools (e.g. `ruff`, `black`).

## Deployment
- Optionally use GitHub Actions or local Quarto to publish the `calendar/_site` folder.

