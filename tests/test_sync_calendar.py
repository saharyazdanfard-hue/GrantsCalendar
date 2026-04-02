import importlib.util
import json
import pathlib
import re
import unittest
from unittest.mock import patch
from urllib.error import HTTPError


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "calendar" / "sync_calendar.py"
SPEC = importlib.util.spec_from_file_location("sync_calendar", MODULE_PATH)
sync_calendar = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(sync_calendar)

INDEX_QMD_PATH = pathlib.Path(__file__).resolve().parents[1] / "calendar" / "index.qmd"


class _MockResponse:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _http_error(url: str, code: int) -> HTTPError:
    return HTTPError(url, code, "error", hdrs=None, fp=None)


class FetchIssueCompletionsTests(unittest.TestCase):
    def test_internal_repo_falls_back_to_zero_when_counts_unavailable(self):
        project = {"githubUrl": "https://github.com/mcphersonlab/internal-repo"}

        def fake_urlopen(request, timeout=30):
            url = request.full_url
            if url.endswith("/graphql"):
                raise _http_error(url, 403)
            if "/repos/mcphersonlab/internal-repo/issues" in url:
                raise _http_error(url, 403)
            if "/search/issues" in url:
                raise _http_error(url, 422)
            if url.endswith("/repos/mcphersonlab/internal-repo"):
                return _MockResponse({"visibility": "internal", "has_issues": True})
            raise AssertionError(f"Unexpected URL: {url}")

        with patch.object(sync_calendar.urllib.request, "urlopen", side_effect=fake_urlopen):
            result = sync_calendar.fetch_issue_completions([project], token="test-token")

        self.assertEqual(result[0]["completionHtml"], "0/0")
        self.assertTrue(result[0]["completionUnavailable"])

    def test_public_repo_with_issues_disabled_falls_back_to_zero(self):
        project = {"githubUrl": "https://github.com/mcphersonlab/no-issues-repo"}

        def fake_urlopen(request, timeout=30):
            url = request.full_url
            if url.endswith("/graphql"):
                raise _http_error(url, 403)
            if "/repos/mcphersonlab/no-issues-repo/issues" in url:
                raise _http_error(url, 410)
            if "/search/issues" in url:
                raise _http_error(url, 422)
            if url.endswith("/repos/mcphersonlab/no-issues-repo"):
                return _MockResponse({"visibility": "public", "has_issues": False})
            raise AssertionError(f"Unexpected URL: {url}")

        with patch.object(sync_calendar.urllib.request, "urlopen", side_effect=fake_urlopen):
            result = sync_calendar.fetch_issue_completions([project], token="test-token")

        self.assertEqual(result[0]["completionHtml"], "0/0")
        self.assertFalse(result[0]["completionUnavailable"])

    def test_unknown_repo_still_renders_unavailable(self):
        project = {"githubUrl": "https://github.com/mcphersonlab/missing-repo"}

        def fake_urlopen(request, timeout=30):
            url = request.full_url
            if url.endswith("/graphql"):
                raise _http_error(url, 403)
            if "/repos/mcphersonlab/missing-repo/issues" in url:
                raise _http_error(url, 404)
            if "/search/issues" in url:
                raise _http_error(url, 422)
            if url.endswith("/repos/mcphersonlab/missing-repo"):
                raise _http_error(url, 404)
            raise AssertionError(f"Unexpected URL: {url}")

        with patch.object(sync_calendar.urllib.request, "urlopen", side_effect=fake_urlopen):
            result = sync_calendar.fetch_issue_completions([project], token="test-token")

        self.assertEqual(result[0]["completionHtml"], "—")

    def test_preserve_unavailable_completion_from_existing_qmd_block(self):
        existing_content = """const activeProjects = [
  { projectHtml:"<a href=\\"https://github.com/mcphersonlab/EarthEpi\\">EarthEpi</a>", questionHtml:"Question", conferenceHtml:"Conference", callHtml:"Call", journalHtml:"Journal", completionHtml:"1/1 (100%)" },
  { projectHtml:"<a href=\\"https://github.com/mcphersonlab/StormPath\\">StormPath</a>", questionHtml:"Question", conferenceHtml:"Conference", callHtml:"Call", journalHtml:"Journal", completionHtml:"—" }
 ];"""
        existing_projects = sync_calendar.parse_existing_active_projects(existing_content)
        projects = [
            {
                "githubUrl": "https://github.com/mcphersonlab/EarthEpi",
                "completionHtml": "0/0",
                "completionUnavailable": True,
            },
            {
                "githubUrl": "https://github.com/mcphersonlab/StormPath",
                "completionHtml": "—",
            },
        ]

        result = sync_calendar.preserve_unavailable_project_completions(
            projects, existing_projects
        )

        self.assertEqual(result[0]["completionHtml"], "1/1 (100%)")
        self.assertEqual(result[1]["completionHtml"], "—")

    def test_preserve_does_not_override_real_zero_zero_values(self):
        existing_projects = [
            {
                "projectHtml": '<a href="https://github.com/mcphersonlab/no-issues-repo">repo</a>',
                "completionHtml": "3/4 (75%)",
            }
        ]
        projects = [
            {
                "githubUrl": "https://github.com/mcphersonlab/no-issues-repo",
                "completionHtml": "0/0",
                "completionUnavailable": False,
            }
        ]

        result = sync_calendar.preserve_unavailable_project_completions(
            projects, existing_projects
        )

        self.assertEqual(result[0]["completionHtml"], "0/0")


class FilterUnlinkedCallsForPapersTests(unittest.TestCase):
    def test_filter_unlinked_calls_for_papers_excludes_linked_urls(self):
        projects = [
            {
                "callHtml": (
                    '<strong><a href="https://example.com/cfp/">'
                    "Linked CFP</a></strong>"
                )
            },
            {"callHtml": "No call link"},
        ]
        call_for_papers = [
            {
                "topic": "Linked",
                "journal": "Journal One",
                "due_date": "2026-04-01",
                "website": "https://example.com/cfp",
            },
            {
                "topic": "Unlinked",
                "journal": "Journal Two",
                "due_date": "2026-05-01",
                "website": "https://example.com/other",
            },
            {
                "topic": "Ongoing",
                "journal": "Journal Three",
                "due_date": sync_calendar.ONGOING_STATUS,
                "website": "https://example.com/ongoing",
            },
            {
                "topic": "Missing deadline",
                "journal": "Journal Four",
                "website": "https://example.com/missing-date",
            },
        ]

        result = sync_calendar.filter_unlinked_calls_for_papers(
            projects, call_for_papers
        )

        self.assertEqual([item["website"] for item in result], ["https://example.com/other"])


class BuildCfpJsTests(unittest.TestCase):
    def test_build_cfp_js_strips_html_from_title_text(self):
        js = sync_calendar.build_cfp_js([
            {
                "topic": (
                    "<a href='https://example.com/cfp' target='_blank'>"
                    "HTML Title</a>"
                ),
                "journal": "Example Journal",
                "impact": "3.2",
                "due_date": "2026-06-30",
                "website": "https://example.com/cfp",
            }
        ])

        self.assertIn('title:"CFP: HTML Title"', js)
        self.assertNotIn("<a href=", js)
        self.assertIn('impact:"3.2"', js)
        self.assertIn('journal:"Example Journal (IF 3.2)"', js)


class TraineeDeadlineCalendarContentTests(unittest.TestCase):
    def test_index_qmd_includes_requested_trainee_program_events(self):
        content = INDEX_QMD_PATH.read_text(encoding="utf-8")

        self.assertIn('id="chk-trainee"', content)
        self.assertIn('category: "trainee"', content)
        self.assertGreater(
            content.index('id="chk-trainee"'),
            content.index('id="chk-venue"'),
        )
        self.assertRegex(
            content,
            re.compile(
                r'traineeDeadlineEvents\.forEach\(e => \{\s+events\.push\(\{\s+'
                r'title: e\.title,\s+start: e\.start,\s+allDay: true,\s+order: 3,',
                re.MULTILINE,
            ),
        )
        self.assertIn('title: `🎓 ${program.title} Opens`', content)
        self.assertIn('title: `🎓 ${program.title} Closes`', content)
        self.assertIn('phase: "Open"', content)
        self.assertIn('phase: "Close"', content)

        for title, opens_on, closes_on in [
            ("MDACC CATALYST Program(s)", "11-17", "01-14"),
            ("McGovern - GradSURP", "12-01", "01-15"),
            ("McGovern - MicroSURP", "12-01", "02-01"),
            ("BCM SMART", "10-01", "01-30"),
            ("UH-CURE/UH-HEART", "12-01", "02-23"),
        ]:
            self.assertIn(
                f'{{ title:"{title}", opensOn:"{opens_on}", closesOn:"{closes_on}" }}',
                content,
            )

    def test_index_qmd_includes_requested_recurring_lab_life_events(self):
        content = INDEX_QMD_PATH.read_text(encoding="utf-8")

        self.assertIn('const recurringLabLifeEvents = [', content)
        self.assertIn(
            '{ title:"🇬🇷 Niko Niko\'s — Greek Independence Day", monthDay:"03-25", details:"Annual Greek Independence Day outing at Niko Niko\'s.", category:"lablife" }',
            content,
        )
        self.assertIn(
            '{ title:"🇲🇽 Hugo\'s — Mexico\'s Independence Day", monthDay:"09-16", details:"Annual Mexico\'s Independence Day outing at Hugo\'s.", category:"lablife" }',
            content,
        )
        self.assertIn(
            '...generateAnnualLabLifeEvents(2025, 2030, recurringLabLifeEvents),',
            content,
        )


if __name__ == "__main__":
    unittest.main()
