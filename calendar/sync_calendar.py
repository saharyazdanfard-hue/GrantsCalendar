"""Sync calendar event data from mcphersonlab/mcphersonlab.github.io into
calendar/index.qmd.

Fetches _conferences_data.py, _callforpapers_data.py, and
_nih_grant_deadlines_data.py from the source repo, converts them to the
JavaScript format expected by calendar/index.qmd, and replaces the
`const conferences`, `const callsForPapers`, `const unlinkedCallsForPapers`,
`const nihGrantDeadlines`, and `const activeProjects` blocks in place.

Also fetches the rendered Active Projects table from
https://mcphersonlab.github.io/research/projects and embeds it as a static
JavaScript array so the table renders without any client-side cross-origin
requests.

Usage:
    python calendar/sync_calendar.py
"""

import ast
import html as _html_module
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from html.parser import HTMLParser as _HTMLParser
from pathlib import Path

# ---------------------------------------------------------------------------
# Source data URLs (raw)
# ---------------------------------------------------------------------------
_BASE_RAW = (
    "https://raw.githubusercontent.com/"
    "mcphersonlab/mcphersonlab.github.io/main/research"
)
CONF_URL = f"{_BASE_RAW}/_conferences_data.py"
CFP_URL  = f"{_BASE_RAW}/_callforpapers_data.py"
NIH_URL  = f"{_BASE_RAW}/_nih_grant_deadlines_data.py"

# Rendered projects page (HTML) — active projects table is extracted from here
PROJECTS_URL = "https://mcphersonlab.github.io/research/projects"

# NIH grant deadlines reference page (linked in event modal)
NIH_REFERENCE_URL = (
    "https://grants.nih.gov/grants-process/submit/submission-policies/"
    "standard-due-dates"
)

# Sentinel value used in the source data for open-ended deadlines
ONGOING_STATUS = "Ongoing"

# Path to the target file, resolved relative to this script's directory
QMD_PATH = Path(__file__).parent / "index.qmd"

# GitHub API endpoints
GITHUB_API_BASE = "https://api.github.com"
GITHUB_GRAPHQL_URL = f"{GITHUB_API_BASE}/graphql"


# ---------------------------------------------------------------------------
# Fetch helpers
# ---------------------------------------------------------------------------

def fetch_text(url: str) -> str:
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except Exception as exc:
        print(f"ERROR fetching {url}: {exc}", file=sys.stderr)
        raise


def parse_data_file(source: str, variable_name: str) -> list:
    """Safely parse a Python data file and return the named list variable.

    Uses ast.parse + ast.literal_eval so only Python literal structures
    (dicts, lists, strings, numbers, booleans, None) are evaluated — no
    arbitrary code is executed even if the remote file is tampered with.
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(t, ast.Name) and t.id == variable_name
                for t in node.targets
            )
        ):
            return ast.literal_eval(node.value)  # type: ignore[arg-type]
    raise ValueError(f"Variable '{variable_name}' not found in source file")


# ---------------------------------------------------------------------------
# Active Projects HTML parser
# ---------------------------------------------------------------------------

class _ActiveProjectsParser(_HTMLParser):
    """Extract rows from the #active-projects-table-wrapper table.

    Preserves safe inline markup (<a>, <strong>, <em>, <br>).  Any other
    elements are rendered as plain text.  Only http/https href values are
    kept; all other attributes are dropped.
    """

    _INLINE_TAGS = frozenset(["a", "strong", "em"])
    # Number of data columns in the active-projects table
    _COLUMN_COUNT = 5

    def __init__(self) -> None:
        super().__init__()
        self._in_wrapper = False
        self._depth_wrapper = 0
        self._in_table = False
        self._depth_table = 0
        self._in_tbody = False
        self._in_tr = False
        self._in_td = False
        # Stack tracks which inline tag was actually opened (None = text-only)
        self._inline_stack: list[str | None] = []
        self.rows: list[list[str]] = []
        self._current_row: list[str] = []
        self._cell_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        a = dict(attrs)

        if not self._in_wrapper:
            if tag == "div" and a.get("id") == "active-projects-table-wrapper":
                self._in_wrapper = True
                self._depth_wrapper = 1
            return

        # Track wrapper <div> depth so we know when we leave it
        if tag == "div":
            self._depth_wrapper += 1
            return

        if not self._in_table:
            if tag == "table":
                self._in_table = True
                self._depth_table = 1
            return

        if tag == "table":
            self._depth_table += 1
        if self._depth_table > 1:
            return  # ignore nested tables

        if tag == "tbody":
            self._in_tbody = True
            return
        if not self._in_tbody:
            return

        if tag == "tr":
            self._in_tr = True
            self._current_row = []
            return
        if not self._in_tr:
            return

        if tag == "td":
            self._in_td = True
            self._cell_parts = []
            self._inline_stack = []
            return
        if not self._in_td:
            return

        # -- inline markup inside a <td> --
        if tag == "br":
            self._cell_parts.append("<br>")
        elif tag == "a":
            href = a.get("href", "")
            parsed = urllib.parse.urlsplit(href)
            if parsed.scheme in ("http", "https") and parsed.netloc:
                safe = _html_module.escape(href, quote=True)
                self._cell_parts.append(
                    f'<a href="{safe}" target="_blank" rel="noopener noreferrer">'
                )
                self._inline_stack.append("a")
            else:
                self._inline_stack.append(None)  # drop href, render text only
        elif tag in ("strong", "em"):
            self._cell_parts.append(f"<{tag}>")
            self._inline_stack.append(tag)
        else:
            self._inline_stack.append(None)

    def handle_endtag(self, tag: str) -> None:
        if not self._in_wrapper:
            return

        if tag == "div":
            self._depth_wrapper -= 1
            if self._depth_wrapper == 0:
                self._in_wrapper = False
            return

        if not self._in_table:
            return

        if tag == "table":
            self._depth_table -= 1
            if self._depth_table == 0:
                self._in_table = False
            return
        if self._depth_table > 1:
            return

        if tag == "tbody":
            self._in_tbody = False
            return
        if not self._in_tbody:
            return

        if tag == "tr" and self._in_tr:
            self._in_tr = False
            if self._current_row:
                self.rows.append(self._current_row[:])
            self._current_row = []
            return
        if not self._in_tr:
            return

        if tag == "td" and self._in_td:
            self._in_td = False
            self._current_row.append("".join(self._cell_parts).strip())
            self._cell_parts = []
            self._inline_stack = []
            return
        if not self._in_td:
            return

        # closing inline tags
        if tag in self._INLINE_TAGS and self._inline_stack:
            opened = self._inline_stack.pop()
            if opened == tag:
                self._cell_parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if self._in_td:
            self._cell_parts.append(_html_module.escape(data))


def parse_active_projects(html_text: str) -> list[dict]:
    """Parse the projects page HTML and return a list of project dicts.

    Each dict has seven keys: projectHtml, questionHtml, conferenceHtml,
    callHtml, journalHtml — each containing sanitised HTML suitable for
    direct use as ``innerHTML`` of a table cell — plus githubUrl, the
    first https://github.com/… URL found in projectHtml (empty string if
    none), and completionHtml, populated later by fetch_issue_completions.
    """
    parser = _ActiveProjectsParser()
    parser.feed(html_text)
    n = _ActiveProjectsParser._COLUMN_COUNT
    projects = []
    for row in parser.rows:
        while len(row) < n:
            row.append("")
        project_html = row[0]
        # Extract the first github.com URL from the project cell;
        # strip any trailing slash so the key is always normalised.
        m = re.search(
            r'href="(https://github\.com/[^/"]+/[^/"]+?)/?"',
            project_html,
        )
        github_url = m.group(1) if m else ""
        projects.append({
            "projectHtml":    project_html,
            "questionHtml":   row[1],
            "conferenceHtml": row[2],
            "callHtml":       row[3],
            "journalHtml":    row[4],
            "githubUrl":      github_url,
            "completionHtml": "",  # populated later by fetch_issue_completions
        })
    return projects


def parse_existing_active_projects(content: str) -> list[dict]:
    """Return the embedded ``activeProjects`` array from ``index.qmd``.

    The generated block is JavaScript object literal syntax with unquoted keys,
    but the values are JSON-compatible. Convert the known keys so the array can
    be parsed with ``json.loads``.
    """
    match = re.search(
        r"const activeProjects = \[\n(.*?)\n\s*\];",
        content,
        flags=re.DOTALL,
    )
    if not match:
        return []

    body = match.group(1).strip()
    if not body:
        return []

    json_body = body
    for field in (
        "projectHtml",
        "questionHtml",
        "conferenceHtml",
        "callHtml",
        "journalHtml",
        "completionHtml",
    ):
        json_body = json_body.replace(f"{field}:", f'"{field}":')

    try:
        data = json.loads(f"[{json_body}]")
    except json.JSONDecodeError:
        return []

    return data if isinstance(data, list) else []


def preserve_unavailable_project_completions(
    projects: list[dict], existing_projects: list[dict]
) -> list[dict]:
    """Keep the last known completion when a refreshed count is unavailable."""
    existing_by_url: dict[str, str] = {}
    for existing in existing_projects:
        project_html = str(existing.get("projectHtml", ""))
        completion_html = str(existing.get("completionHtml", "")).strip()
        if not completion_html or completion_html == "—":
            continue
        match = re.search(
            r'href="(https://github\.com/[^/"]+/[^/"]+?)/?"',
            project_html,
        )
        if match:
            existing_by_url[match.group(1)] = completion_html

    for project in projects:
        if (
            project.get("completionHtml") == "—"
            or project.get("completionUnavailable") is True
        ):
            previous = existing_by_url.get(str(project.get("githubUrl", "")))
            if previous:
                project["completionHtml"] = previous

    return projects


def normalize_matching_url(url: str) -> str:
    """Normalize a URL for matching equivalent CFP links."""
    trimmed = str(url).strip()
    if not trimmed:
        return ""
    parsed = urllib.parse.urlsplit(trimmed)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return ""
    normalized_path = parsed.path.rstrip("/")
    return urllib.parse.urlunsplit((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        normalized_path,
        parsed.query,
        "",
    ))


def filter_unlinked_calls_for_papers(
    projects: list[dict],
    call_for_papers: list[dict],
) -> list[dict]:
    """Return deadline-based CFPs whose website is not linked from a project call."""
    linked_urls = set()
    for project in projects:
        for href in re.findall(r'href="([^"]+)"', project.get("callHtml", "")):
            normalized = normalize_matching_url(href)
            if normalized:
                linked_urls.add(normalized)

    unlinked = []
    for cfp in call_for_papers:
        if not has_cfp_deadline(cfp):
            continue
        website = normalize_matching_url(cfp.get("website", ""))
        if website and website in linked_urls:
            continue
        unlinked.append(cfp)

    return unlinked


# ---------------------------------------------------------------------------
# GitHub issue completion
# ---------------------------------------------------------------------------

def _make_github_request(
    url: str,
    *,
    token: str,
    data: bytes | None = None,
    method: str = "GET",
) -> urllib.request.Request:
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    return req


def _fetch_issue_count_search(
    owner: str, repo: str, state: str, token: str
) -> int:
    """Return the number of issues in ``state`` via the Search API.

    Uses the Search API with ``type:issue`` so that pull requests are
    excluded from the count.  Returns ``-1`` on error.
    """
    query = f"repo:{owner}/{repo} type:issue state:{state}"
    encoded_query = urllib.parse.quote_plus(query)
    url = f"{GITHUB_API_BASE}/search/issues?q={encoded_query}"

    def _request_with_token(request_token: str) -> int:
        req = _make_github_request(url, token=request_token)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return int(data.get("total_count", 0))

    try:
        return _request_with_token(token)
    except urllib.error.HTTPError as exc:
        if token and exc.code in (401, 403):
            # Some tokens may not be accepted for this endpoint; retrying
            # unauthenticated still preserves public repo completion counts.
            print(
                f"  WARNING: Search API returned HTTP {exc.code} for "
                f"{owner}/{repo}; retrying unauthenticated",
                file=sys.stderr,
            )
            try:
                return _request_with_token("")
            except (
                urllib.error.HTTPError,
                urllib.error.URLError,
                TimeoutError,
            ) as retry_exc:
                print(
                    f"  WARNING: Could not fetch issues ({state}) for "
                    f"{owner}/{repo}: {retry_exc}",
                    file=sys.stderr,
                )
                return -1

        print(
            f"  WARNING: Could not fetch issues ({state}) for "
            f"{owner}/{repo}: {exc}",
            file=sys.stderr,
        )
        return -1
    except Exception as exc:
        print(
            f"  WARNING: Could not fetch issues ({state}) for "
            f"{owner}/{repo}: {exc}",
            file=sys.stderr,
        )
        return -1


def _fetch_issue_count_repo_issues(
    owner: str, repo: str, state: str, token: str
) -> int:
    """Return issue count in ``state`` via ``/repos/{owner}/{repo}/issues``.

    Uses token-authenticated repo issue listing, which supports internal repos
    when the token has repository access. Pull requests are excluded from the
    count.
    """
    if not token:
        return -1

    total = 0
    page = 1
    per_page = 100
    while True:
        params = urllib.parse.urlencode(
            {"state": state, "page": page, "per_page": per_page}
        )
        url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues?{params}"
        req = _make_github_request(url, token=token)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                issues = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            print(
                f"  WARNING: Could not fetch issues ({state}) for "
                f"{owner}/{repo} via repo endpoint: {exc}",
                file=sys.stderr,
            )
            return -1

        if not isinstance(issues, list) or not issues:
            break

        total += sum(1 for item in issues if item.get("pull_request") is None)
        if len(issues) < per_page:
            break
        page += 1

    return total


def _fetch_repo_metadata(owner: str, repo: str, token: str) -> dict | None:
    """Return repository metadata from ``/repos/{owner}/{repo}``.

    Used to distinguish inaccessible internal/private repos from broken links
    when issue counts cannot be fetched directly.
    """
    if not token:
        return None

    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
    req = _make_github_request(url, token=token)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(
            f"  WARNING: Could not fetch repository metadata for "
            f"{owner}/{repo}: {exc}",
            file=sys.stderr,
        )
        return None

    if not isinstance(data, dict):
        return None
    return data


def fetch_issue_completions(
    projects: list[dict], token: str
) -> list[dict]:
    """Add ``completionHtml`` to each project dict.

    Fetches open and closed issue counts for every project that has a
    ``githubUrl`` pointing to a GitHub repository.  With a token the
    GraphQL API is used (one round-trip for all repos). Missing repos then
    use token-authenticated /repos/{owner}/{repo}/issues listing (supports
    internal repos), with Search API as the final fallback.

    Projects whose repos cannot be reached get ``completionHtml = "—"``.
    """
    # Collect repos that have a GitHub URL
    repo_entries: list[tuple[int, str, str]] = []  # (index, owner, repo)
    for i, p in enumerate(projects):
        url = p.get("githubUrl", "")
        m = re.match(r"https://github\.com/([^/]+)/([^/]+?)/?$", url)
        if m:
            repo_entries.append((i, m.group(1), m.group(2)))

    if not repo_entries:
        return projects

    # ── GraphQL (batched, requires token) ──────────────────────────────
    counts: dict[str, tuple[int, int, bool]] = {}
    # "owner/repo" -> (closed, total, unavailable)
    rest_token = token  # token used for the Search API fallback

    if token:
        aliases: list[str] = []
        alias_map: dict[str, tuple[str, str]] = {}
        for idx, (_, owner, repo) in enumerate(repo_entries):
            alias = f"r{idx}"
            alias_map[alias] = (owner, repo)
            aliases.append(
                f"  {alias}: repository("
                f'owner: {json.dumps(owner)}, name: {json.dumps(repo)}) {{\n'
                f"    open:   issues(states: [OPEN])   {{ totalCount }}\n"
                f"    closed: issues(states: [CLOSED]) {{ totalCount }}\n"
                f"  }}"
            )
        query = "{\n" + "\n".join(aliases) + "\n}"
        req = _make_github_request(
            GITHUB_GRAPHQL_URL,
            token=token,
            data=json.dumps({"query": query}).encode("utf-8"),
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            gql_data = result.get("data") or {}
            for alias, repo_data in gql_data.items():
                if not repo_data:
                    continue
                owner, repo = alias_map[alias]
                closed = repo_data.get("closed", {}).get("totalCount", 0)
                open_c = repo_data.get("open", {}).get("totalCount", 0)
                counts[f"{owner}/{repo}"] = (closed, closed + open_c, False)
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                # Token may not be accepted for GraphQL; keep it for the
                # Search API fallback since it may still allow internal repos.
                print(
                    f"  WARNING: GraphQL request returned HTTP {exc.code} "
                    "(token lacks GraphQL access); falling back to Search API",
                    file=sys.stderr,
                )
            else:
                print(
                    f"  WARNING: GraphQL batch request failed (HTTP {exc.code}); "
                    "falling back to Search API",
                    file=sys.stderr,
                )
            counts = {}  # will fall through to Search API below (both branches)
        except Exception as exc:
            print(
                f"  WARNING: GraphQL batch request failed: {exc}; "
                "falling back to Search API",
                file=sys.stderr,
            )
            counts = {}  # will fall through to Search API below

    # ── Search API fallback (one request per repo per state) ───────────
    missing = [
        (i, owner, repo)
        for i, owner, repo in repo_entries
        if f"{owner}/{repo}" not in counts
    ]
    repo_metadata_cache: dict[str, dict | None] = {}

    for _, owner, repo in missing:
        key = f"{owner}/{repo}"
        closed = _fetch_issue_count_repo_issues(owner, repo, "closed", rest_token)
        open_c = _fetch_issue_count_repo_issues(owner, repo, "open", rest_token)
        if closed < 0:
            closed = _fetch_issue_count_search(owner, repo, "closed", rest_token)
        if open_c < 0:
            open_c = _fetch_issue_count_search(owner, repo, "open", rest_token)
        if closed < 0 or open_c < 0:
            if key not in repo_metadata_cache:
                repo_metadata_cache[key] = _fetch_repo_metadata(
                    owner, repo, rest_token
                )

            repo_metadata = repo_metadata_cache[key] or {}
            visibility = str(repo_metadata.get("visibility") or "").lower()
            has_issues = repo_metadata.get("has_issues")
            if has_issues is False or visibility in {"internal", "private"}:
                counts[key] = (0, 0, has_issues is not False)
            else:
                counts[key] = (-1, -1, True)
        else:
            counts[key] = (closed, closed + open_c, False)

    # ── Attach completionHtml ──────────────────────────────────────────
    for i, owner, repo in repo_entries:
        closed, total, unavailable = counts.get(f"{owner}/{repo}", (-1, -1, True))
        projects[i]["completionUnavailable"] = unavailable
        if closed < 0 or total < 0:
            projects[i]["completionHtml"] = "—"
        elif total == 0:
            projects[i]["completionHtml"] = "0/0"
        else:
            pct = round(100 * closed / total)
            projects[i]["completionHtml"] = f"{closed}/{total} ({pct}%)"

    return projects


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def add_days(date_str: str, n: int) -> str:
    """Return date_str + n days as a YYYY-MM-DD string."""
    d = datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=n)
    return d.strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# JavaScript generation
# ---------------------------------------------------------------------------

def to_js_str(v) -> str:
    """JSON-encode a value as a JavaScript literal and escape `</` for <script> safety."""
    s = json.dumps(v, ensure_ascii=False)
    # Prevent `</script>` (or similar) from terminating a surrounding <script> block
    return s.replace("</", "<\\/")


def strip_html_tags(value: str) -> str:
    """Return value with simple HTML tags removed."""
    return re.sub(r"<[^>]+>", "", str(value)).strip()


def has_cfp_deadline(call_for_paper: dict) -> bool:
    """Return True when the CFP has a concrete deadline date."""
    due_date = str(call_for_paper.get("due_date", "")).strip()
    return bool(due_date) and due_date != ONGOING_STATUS


def build_conferences_js(conferences: list) -> str:
    """Generate the `const conferences = [...];` JS block."""
    lines = ["const conferences = ["]
    for i, c in enumerate(conferences):
        comma = "," if i < len(conferences) - 1 else ""

        name    = c.get("name", "")
        start   = c.get("start_date", "")
        end_raw = c.get("end_date", "")
        # FullCalendar end is exclusive — add 1 day to the actual last day
        end     = add_days(end_raw, 1) if end_raw else ""
        loc     = c.get("location", "")
        url     = c.get("url", "")
        cfp_open  = c.get("abstract_open", "")
        cfp_close = c.get("abstract_close", "")
        cfp_note  = c.get("abstract_note", "")

        fields = [
            f"title:{to_js_str(name)}",
            f"start:{to_js_str(start)}",
            f"end:{to_js_str(end)}",
        ]
        if loc:
            fields.append(f"location:{to_js_str(loc)}")
        if url:
            fields.append(f"url:{to_js_str(url)}")
        if cfp_open:
            fields.append(f"cfpOpen:{to_js_str(cfp_open)}")
        if cfp_close:
            fields.append(f"cfpClose:{to_js_str(cfp_close)}")
        if cfp_note:
            fields.append(f"cfpNote:{to_js_str(cfp_note)}")

        lines.append(f"  {{ {', '.join(fields)} }}{comma}")

    lines.append("];")
    return "\n".join(lines)


def build_cfp_js(call_for_papers: list) -> str:
    """Generate the `const callsForPapers = [...];` JS block."""
    valid = [
        c for c in call_for_papers
        if has_cfp_deadline(c)
    ]

    lines = ["const callsForPapers = ["]
    for i, c in enumerate(valid):
        comma = "," if i < len(valid) - 1 else ""

        journal = c.get("journal", "")
        impact  = c.get("impact", "")
        topic   = strip_html_tags(c.get("topic", ""))
        date    = c.get("due_date", "")
        website = c.get("website", "")

        # Title shown on the calendar tile
        title = f"CFP: {topic}" if topic else f"CFP: {journal}"
        # Journal field shown in the modal detail popup
        journal_display = f"{journal} (IF {impact})" if impact else journal

        fields = [
            f"title:{to_js_str(title)}",
            f"journal:{to_js_str(journal_display)}",
            f"impact:{to_js_str(impact)}",
            f"date:{to_js_str(date)}",
            f"url:{to_js_str(website)}",
        ]
        lines.append(f"  {{ {', '.join(fields)} }}{comma}")

    lines.append("];")
    return "\n".join(lines)


def build_unlinked_cfp_js(call_for_papers: list) -> str:
    """Generate the `const unlinkedCallsForPapers = [...];` JS block."""
    block = build_cfp_js(call_for_papers)
    return block.replace("const callsForPapers =", "const unlinkedCallsForPapers =", 1)


def build_nih_js(nih_grant_deadlines: list) -> str:
    """Generate the `const nihGrantDeadlines = [...];` JS block.

    Expands each recurring entry (which lists MM-DD month_days) into concrete
    dated events for the current year and the following two years, so the
    calendar always has adequate forward coverage after each daily sync.
    """
    current_year = date.today().year
    years = [current_year, current_year + 1, current_year + 2]

    events: list[dict] = []
    for item in nih_grant_deadlines:
        label  = item.get("label", "")
        detail = item.get("detail", "")
        note   = item.get("note", "")
        for year in years:
            for mm_dd in item.get("month_days", []):
                events.append({
                    "title":  f"🏛️ {label}",
                    "date":   f"{year}-{mm_dd}",
                    "detail": detail,
                    "note":   note,
                    "url":    NIH_REFERENCE_URL,
                })

    lines = ["const nihGrantDeadlines = ["]
    for i, e in enumerate(events):
        comma = "," if i < len(events) - 1 else ""
        fields = [
            f"title:{to_js_str(e['title'])}",
            f"date:{to_js_str(e['date'])}",
            f"detail:{to_js_str(e['detail'])}",
            f"note:{to_js_str(e['note'])}",
            f"url:{to_js_str(e['url'])}",
        ]
        lines.append(f"  {{ {', '.join(fields)} }}{comma}")
    lines.append("];")
    return "\n".join(lines)


def build_projects_js(projects: list[dict]) -> str:
    """Generate the `const activeProjects = [...];` JS block."""
    lines = ["const activeProjects = ["]
    for i, p in enumerate(projects):
        comma = "," if i < len(projects) - 1 else ""
        fields = [
            f"projectHtml:{to_js_str(p['projectHtml'])}",
            f"questionHtml:{to_js_str(p['questionHtml'])}",
            f"conferenceHtml:{to_js_str(p['conferenceHtml'])}",
            f"callHtml:{to_js_str(p['callHtml'])}",
            f"journalHtml:{to_js_str(p['journalHtml'])}",
            f"completionHtml:{to_js_str(p.get('completionHtml', ''))}",
        ]
        lines.append(f"  {{ {', '.join(fields)} }}{comma}")
    lines.append("];")
    return "\n".join(lines)


def replace_js_block(content: str, block_name: str, new_block: str) -> str:
    """Replace a `const <block_name> = [...];` block with new_block.

    The replacement scans line-by-line:
    - Finds the line starting with `const <block_name> = [`
    - Scans forward until a line whose stripped form equals `];`
    - Replaces the entire range (inclusive) with the new block lines.
    """
    lines = content.split("\n")
    start_prefix = f"const {block_name} = ["

    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith(start_prefix):
            start_idx = i
            break

    if start_idx is None:
        raise ValueError(
            f"Could not find 'const {block_name} = [' in {QMD_PATH}"
        )

    end_idx = None
    for i in range(start_idx + 1, len(lines)):
        if lines[i].strip() == "];":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError(
            f"Could not find closing '];' for '{block_name}' in {QMD_PATH}"
        )

    new_lines = lines[:start_idx] + new_block.split("\n") + lines[end_idx + 1:]
    return "\n".join(new_lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    content = QMD_PATH.read_text(encoding="utf-8")
    existing_projects = parse_existing_active_projects(content)

    print("Fetching conference data from mcphersonlab.github.io …")
    conferences = parse_data_file(fetch_text(CONF_URL), "conferences")
    print(f"  Loaded {len(conferences)} conferences")

    print("Fetching call-for-papers data from mcphersonlab.github.io …")
    cfps = parse_data_file(fetch_text(CFP_URL), "call_for_papers")
    print(f"  Loaded {len(cfps)} calls for papers")

    print("Fetching NIH grant deadlines data from mcphersonlab.github.io …")
    nih_deadlines = parse_data_file(fetch_text(NIH_URL), "nih_grant_deadlines")
    print(f"  Loaded {len(nih_deadlines)} NIH deadline series")

    print("Fetching active projects table from mcphersonlab.github.io …")
    projects = parse_active_projects(fetch_text(PROJECTS_URL))
    print(f"  Loaded {len(projects)} active projects")

    unlinked_cfps = filter_unlinked_calls_for_papers(projects, cfps)
    print(f"  Found {len(unlinked_cfps)} calls for papers without linked projects")

    print("Fetching GitHub issue completion data …")
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print(
            "  WARNING: GITHUB_TOKEN not set — "
            "falling back to unauthenticated REST API (may be slower or "
            "rate-limited for large project lists)",
            file=sys.stderr,
        )
    projects = fetch_issue_completions(projects, token)
    projects = preserve_unavailable_project_completions(
        projects, existing_projects
    )
    print("  Done fetching issue counts")

    content = replace_js_block(content, "conferences",       build_conferences_js(conferences))
    content = replace_js_block(content, "callsForPapers",    build_cfp_js(cfps))
    content = replace_js_block(content, "unlinkedCallsForPapers", build_unlinked_cfp_js(unlinked_cfps))
    content = replace_js_block(content, "nihGrantDeadlines", build_nih_js(nih_deadlines))
    content = replace_js_block(content, "activeProjects",    build_projects_js(projects))

    QMD_PATH.write_text(content, encoding="utf-8")
    print(f"Done — {QMD_PATH} updated")


if __name__ == "__main__":
    main()
