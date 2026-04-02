"""Sync calendar event data into calendar/index.qmd.

This script aggregates events from various calendar sources and converts them
to the JavaScript format expected by calendar/index.qmd. Events are inserted
into the `const events` block defined in the template.

Supported sources:
- Local JSON files with event data
- Custom Python functions that return event lists
- ICS calendar files

Usage:
    python calendar/sync_calendar.py

Configuration:
    Edit the CALENDAR_SOURCES section below to add your calendar sources.
"""

import json
import re
import sys
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Path to the target file, resolved relative to this script's directory
QMD_PATH = Path(__file__).parent / "index.qmd"

# Calendar sources configuration
# Each source should return a list of event dictionaries
CALENDAR_SOURCES: List[Callable[[], List[Dict[str, Any]]]] = [
    # Add your calendar source functions here
    # Example: get_google_calendar_events, get_local_events, etc.
]

# Event categories and their display properties
EVENT_CATEGORIES = {
    "work": {"color": "#3788d8", "label": "Work"},
    "personal": {"color": "#78d854", "label": "Personal"},
    "reminder": {"color": "#f59e0b", "label": "Reminder"},
    "birthday": {"color": "#ec4899", "label": "Birthday"},
    "holiday": {"color": "#8b5cf6", "label": "Holiday"},
    "travel": {"color": "#06b6d4", "label": "Travel"},
    "other": {"color": "#6b7280", "label": "Other"},
}


# ---------------------------------------------------------------------------
# Event helpers
# ---------------------------------------------------------------------------

def normalize_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize an event to the standard format.
    
    Required fields:
    - id: unique identifier
    - title: event title
    - start: ISO 8601 datetime string
    
    Optional fields:
    - end: ISO 8601 datetime string
    - category: event category (default: "other")
    - description: event description
    - url: event URL
    """
    required = ["id", "title", "start"]
    for field in required:
        if field not in event:
            raise ValueError(f"Event missing required field: {field}")
    
    normalized = {
        "id": str(event["id"]),
        "title": str(event["title"]),
        "start": str(event["start"]),
    }
    
    if "end" in event:
        normalized["end"] = str(event["end"])
    
    if "category" in event:
        category = event["category"]
        if category not in EVENT_CATEGORIES:
            print(f"Warning: unknown category '{category}', using 'other'", file=sys.stderr)
            category = "other"
        normalized["category"] = category
    else:
        normalized["category"] = "other"
    
    if "description" in event:
        normalized["description"] = str(event["description"])
    
    if "url" in event:
        normalized["url"] = str(event["url"])
    
    return normalized


def get_sample_events() -> List[Dict[str, Any]]:
    """Return sample events for demonstration.
    
    Replace this with actual calendar source integrations.
    """
    return [
        {
            "id": "sample-1",
            "title": "Sample Event",
            "start": "2026-04-15T10:00:00",
            "end": "2026-04-15T11:00:00",
            "category": "personal",
            "description": "This is a sample event. Replace with your calendar data.",
        }
    ]


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def aggregate_events() -> List[Dict[str, Any]]:
    """Aggregate events from all configured calendar sources."""
    all_events = []
    
    # Add events from configured sources
    for source_func in CALENDAR_SOURCES:
        try:
            events = source_func()
            all_events.extend(events)
        except Exception as e:
            print(f"Error fetching events from {source_func.__name__}: {e}", file=sys.stderr)
            continue
    
    # Add sample events if no sources are configured
    if not CALENDAR_SOURCES:
        all_events.extend(get_sample_events())
    
    # Normalize all events
    normalized = []
    for event in all_events:
        try:
            normalized.append(normalize_event(event))
        except ValueError as e:
            print(f"Skipping invalid event: {e}", file=sys.stderr)
            continue
    
    # Sort by start date
    normalized.sort(key=lambda e: e["start"])
    
    return normalized


# ---------------------------------------------------------------------------
# Template generation
# ---------------------------------------------------------------------------

def generate_events_js(events: List[Dict[str, Any]]) -> str:
    """Generate JavaScript code for events array."""
    json_str = json.dumps(events, indent=2)
    return f"const events = {json_str};"


# ---------------------------------------------------------------------------
# File manipulation
# ---------------------------------------------------------------------------

def read_template() -> str:
    """Read the current template file."""
    try:
        return QMD_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"ERROR: Template file not found: {QMD_PATH}", file=sys.stderr)
        sys.exit(1)


def write_template(content: str) -> None:
    """Write the updated template file."""
    try:
        QMD_PATH.write_text(content, encoding="utf-8")
    except Exception as e:
        print(f"ERROR writing to {QMD_PATH}: {e}", file=sys.stderr)
        sys.exit(1)


def update_events_in_template(content: str, events_js: str) -> str:
    """Replace the events JavaScript block in the template."""
    # Look for the existing const events block and replace it
    pattern = r"const events = \[.*?\];"
    
    if re.search(pattern, content, re.DOTALL):
        return re.sub(pattern, events_js, content, flags=re.DOTALL)
    else:
        # If no existing block, try to insert before the calendar initialization
        # Look for a good insertion point
        if "document.addEventListener" in content or "FullCalendar" in content:
            # Insert before calendar initialization
            insert_point = content.find("document.addEventListener")
            if insert_point == -1:
                insert_point = content.find("FullCalendar")
            if insert_point != -1:
                # Find the last newline before this point
                insert_point = content.rfind("\n", 0, insert_point) + 1
                return (
                    content[:insert_point] + 
                    events_js + "\n\n" +
                    content[insert_point:]
                )
        
        # If no good insertion point found, just append before closing script tag
        if "</script>" in content:
            return content.replace("</script>", f"\n{events_js}\n</script>", 1)
        
        # Last resort: append at the end
        return content + f"\n{events_js}\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Main entry point."""
    print("📅 Syncing calendar events...", file=sys.stderr)
    
    try:
        # Aggregate events from all sources
        events = aggregate_events()
        print(f"✓ Aggregated {len(events)} events", file=sys.stderr)
        
        # Generate JavaScript
        events_js = generate_events_js(events)
        
        # Read template
        template = read_template()
        
        # Update template with new events
        updated_template = update_events_in_template(template, events_js)
        
        # Write updated template
        write_template(updated_template)
        print(f"✓ Updated {QMD_PATH}", file=sys.stderr)
        print("✓ Sync complete!", file=sys.stderr)
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
