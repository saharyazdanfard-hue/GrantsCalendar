import importlib.util
import json
import pathlib
import unittest
from unittest.mock import MagicMock


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "calendar" / "sync_calendar.py"
SPEC = importlib.util.spec_from_file_location("sync_calendar", MODULE_PATH)
sync_calendar = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(sync_calendar)


class NormalizeEventTests(unittest.TestCase):
    """Test event normalization."""

    def test_normalize_event_with_required_fields(self):
        event = {
            "id": "event-1",
            "title": "Test Event",
            "start": "2026-04-15T10:00:00",
        }
        result = sync_calendar.normalize_event(event)
        self.assertEqual(result["id"], "event-1")
        self.assertEqual(result["title"], "Test Event")
        self.assertEqual(result["start"], "2026-04-15T10:00:00")
        self.assertEqual(result["category"], "other")

    def test_normalize_event_with_optional_fields(self):
        event = {
            "id": "event-1",
            "title": "Test Event",
            "start": "2026-04-15T10:00:00",
            "end": "2026-04-15T11:00:00",
            "category": "work",
            "description": "A test event",
            "url": "https://example.com",
        }
        result = sync_calendar.normalize_event(event)
        self.assertEqual(result["end"], "2026-04-15T11:00:00")
        self.assertEqual(result["category"], "work")
        self.assertEqual(result["description"], "A test event")
        self.assertEqual(result["url"], "https://example.com")

    def test_normalize_event_missing_required_field(self):
        event = {
            "title": "Test Event",
            "start": "2026-04-15T10:00:00",
        }
        with self.assertRaises(ValueError):
            sync_calendar.normalize_event(event)

    def test_normalize_event_invalid_category(self):
        event = {
            "id": "event-1",
            "title": "Test Event",
            "start": "2026-04-15T10:00:00",
            "category": "invalid",
        }
        # Should default to "other" when category is invalid
        result = sync_calendar.normalize_event(event)
        # The function warns but defaults to "other"
        self.assertEqual(result["category"], "other")


class AggregateEventsTests(unittest.TestCase):
    """Test event aggregation."""

    def test_aggregate_events_empty_sources(self):
        # When no sources are configured, should use sample events
        original_sources = sync_calendar.CALENDAR_SOURCES
        sync_calendar.CALENDAR_SOURCES = []
        try:
            events = sync_calendar.aggregate_events()
            self.assertGreater(len(events), 0)
        finally:
            sync_calendar.CALENDAR_SOURCES = original_sources

    def test_aggregate_events_with_source(self):
        def test_source():
            return [
                {
                    "id": "event-1",
                    "title": "Event 1",
                    "start": "2026-04-15T10:00:00",
                    "category": "personal",
                },
                {
                    "id": "event-2",
                    "title": "Event 2",
                    "start": "2026-04-20T14:00:00",
                    "category": "work",
                },
            ]

        original_sources = sync_calendar.CALENDAR_SOURCES
        sync_calendar.CALENDAR_SOURCES = [test_source]
        try:
            events = sync_calendar.aggregate_events()
            self.assertEqual(len(events), 2)
            self.assertEqual(events[0]["title"], "Event 1")
            self.assertEqual(events[1]["title"], "Event 2")
            # Events should be sorted by start date
            self.assertTrue(events[0]["start"] <= events[1]["start"])
        finally:
            sync_calendar.CALENDAR_SOURCES = original_sources


class GenerateEventsJsTests(unittest.TestCase):
    """Test JavaScript generation."""

    def test_generate_events_js(self):
        events = [
            {
                "id": "1",
                "title": "Event 1",
                "start": "2026-04-15",
                "category": "personal",
            }
        ]
        result = sync_calendar.generate_events_js(events)
        self.assertTrue(result.startswith("const events = "))
        self.assertTrue(result.endswith(";"))
        # Should contain JSON
        self.assertIn("Event 1", result)


class EventCategoriesTests(unittest.TestCase):
    """Test event category configuration."""

    def test_event_categories_exist(self):
        expected_categories = [
            "work",
            "personal",
            "reminder",
            "birthday",
            "holiday",
            "travel",
            "other",
        ]
        for cat in expected_categories:
            self.assertIn(cat, sync_calendar.EVENT_CATEGORIES)


class TemplateUpdateTests(unittest.TestCase):
    """Test template update functionality."""

    def test_update_events_in_template_replace_existing(self):
        template = """
Some content
const events = [{id: "old"}];
More content
"""
        events_js = 'const events = [{id: "new"}];'
        result = sync_calendar.update_events_in_template(template, events_js)
        self.assertIn('const events = [{id: "new"}];', result)
        self.assertNotIn('const events = [{id: "old"}];', result)

    def test_update_events_in_template_insert_new(self):
        template = "<html><body></body></html>"
        events_js = 'const events = []'
        result = sync_calendar.update_events_in_template(template, events_js)
        self.assertIn("const events = []", result)


if __name__ == "__main__":
    unittest.main()
