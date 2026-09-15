import threading
from datetime import datetime
from html import escape
from pathlib import Path


class LogCollector:
    """Thread-safe store for per-test browser JavaScript console messages."""

    def __init__(self):
        self._lock = threading.Lock()
        self._logs: dict[str, list] = {}

    def add(self, node_id: str, log_type: str, message: str):
        entry = {
            "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "type": log_type,
            "message": message,
        }
        with self._lock:
            self._logs.setdefault(node_id, []).append(entry)

    def get(self, node_id: str) -> list:
        with self._lock:
            return list(self._logs.get(node_id, []))


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #0f1117; color: #e2e8f0; min-height: 100vh;
}
/* ---- header ---- */
.header {
  background: linear-gradient(135deg, #1a1f2e 0%, #0f1117 100%);
  border-bottom: 1px solid #2d3748; padding: 24px 32px;
}
.header h1 { font-size: 1.8rem; font-weight: 700; color: #fff; letter-spacing: -0.5px; }
.header h1 span { color: #667eea; }
.header .meta { color: #718096; font-size: 0.85rem; margin-top: 4px; }
/* ---- layout ---- */
.container { max-width: 1200px; margin: 0 auto; padding: 24px 32px; }
/* ---- summary cards ---- */
.summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; margin-bottom: 24px; }
.card {
  background: #1a1f2e; border: 1px solid #2d3748; border-radius: 12px;
  padding: 20px; text-align: center;
}
.card .count { font-size: 2.5rem; font-weight: 800; line-height: 1; }
.card .label { font-size: 0.8rem; color: #718096; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
.card.total  .count { color: #e2e8f0; }
.card.passed .count { color: #68d391; }
.card.failed .count { color: #fc8181; }
.card.skipped .count { color: #f6ad55; }
.card.xfailed .count { color: #b794f4; }
.card.xpassed .count { color: #f687b3; }
/* ---- filters ---- */
.filters { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; align-items: center; }
.filters label { color: #718096; font-size: 0.85rem; margin-right: 4px; }
.filter-btn {
  padding: 6px 16px; border-radius: 20px; border: 1px solid #2d3748;
  background: #1a1f2e; color: #a0aec0; cursor: pointer; font-size: 0.82rem; transition: all .2s;
}
.filter-btn:hover  { background: #2d3748; color: #e2e8f0; border-color: #4a5568; }
.filter-btn.active { background: #2d3748; color: #e2e8f0; border-color: #4a5568; }
.filter-btn.active.all  { border-color: #667eea; color: #667eea; }
.filter-btn.active.pass { border-color: #68d391; color: #68d391; }
.filter-btn.active.fail { border-color: #fc8181; color: #fc8181; }
.filter-btn.active.skip { border-color: #f6ad55; color: #f6ad55; }
.filter-btn.active.xfail { border-color: #b794f4; color: #b794f4; }
.filter-btn.active.xpass { border-color: #f687b3; color: #f687b3; }
.search-box { margin-left: auto; }
.search-box input {
  background: #1a1f2e; border: 1px solid #2d3748; color: #e2e8f0;
  padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; width: 220px; outline: none;
}
.search-box input:focus { border-color: #667eea; }
/* ---- test cards ---- */
.test-card {
  background: #1a1f2e; border: 1px solid #2d3748; border-radius: 10px;
  margin-bottom: 8px; overflow: hidden; transition: border-color .2s;
}
.test-card:hover { border-color: #4a5568; }
.test-card.pass  { border-left: 3px solid #68d391; }
.test-card.fail  { border-left: 3px solid #fc8181; }
.test-card.skip  { border-left: 3px solid #f6ad55; }
.test-card.xfail { border-left: 3px solid #b794f4; }
.test-card.xpass { border-left: 3px solid #f687b3; }
.test-header {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 16px; cursor: pointer; user-select: none;
}
.status-badge {
  padding: 2px 8px; border-radius: 4px; font-size: 0.7rem;
  font-weight: 700; letter-spacing: .5px; flex-shrink: 0;
}
.status-badge.pass  { background: #22543d; color: #68d391; }
.status-badge.fail  { background: #742a2a; color: #fc8181; }
.status-badge.skip  { background: #7b341e; color: #f6ad55; }
.status-badge.xfail { background: #3c2a5a; color: #b794f4; }
.status-badge.xpass { background: #5a2a44; color: #f687b3; }
.test-name     { flex: 1; font-size: 0.9rem; color: #e2e8f0; }
.test-duration { font-size: 0.8rem; color: #718096; flex-shrink: 0; }
.chevron       { color: #4a5568; font-size: 0.8rem; flex-shrink: 0; transition: transform .2s; }
.chevron.open  { transform: rotate(180deg); }
/* ---- test body ---- */
.test-body { padding: 0 16px 16px; }
.test-module {
  font-size: 0.75rem; color: #718096; font-family: 'Courier New', monospace;
  margin-bottom: 12px; padding: 6px 8px; background: #0f1117; border-radius: 4px;
}
.error-msg { margin-bottom: 12px; }
.error-msg pre {
  background: #2d1b1b; border: 1px solid #742a2a; border-radius: 6px;
  padding: 12px; font-size: 0.78rem; color: #fc8181;
  white-space: pre-wrap; word-break: break-all; max-height: 200px; overflow-y: auto;
}
/* ---- logs ---- */
.logs-section {
  background: #0f1117; border: 1px solid #2d3748; border-radius: 8px; overflow: hidden;
}
.logs-header {
  padding: 8px 12px; background: #1a1f2e;
  border-bottom: 1px solid #2d3748; font-size: 0.8rem; color: #718096;
  display: flex; justify-content: space-between; align-items: center;
}
.logs-title { font-weight: 600; }
.log-level-filters { display: flex; gap: 6px; }
.log-filter-btn {
  padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; cursor: pointer;
  border: 1px solid transparent; background: #0f1117; color: #718096; transition: all .15s;
}
.log-filter-btn.active-error { border-color: #fc8181; color: #fc8181; }
.log-filter-btn.active-warn  { border-color: #f6ad55; color: #f6ad55; }
.log-filter-btn.active-info  { border-color: #63b3ed; color: #63b3ed; }
.log-filter-btn.active-log   { border-color: #a0aec0; color: #a0aec0; }
.log-entries { max-height: 320px; overflow-y: auto; }
.log-entry {
  display: flex; gap: 8px; padding: 5px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  font-family: 'Courier New', monospace; font-size: 0.78rem; align-items: flex-start;
}
.log-entry:last-child { border-bottom: none; }
.log-entry.log-error { background: rgba(252,129,129,0.05); }
.log-entry.log-warn  { background: rgba(246,173,85,0.05); }
.log-entry.log-info  { background: rgba(99,179,237,0.04); }
.log-entry.log-debug { background: transparent; }
.log-time    { color: #4a5568; flex-shrink: 0; min-width: 85px; }
.log-level   { font-weight: 700; flex-shrink: 0; min-width: 65px; }
.log-entry.log-error .log-level { color: #fc8181; }
.log-entry.log-warn  .log-level { color: #f6ad55; }
.log-entry.log-info  .log-level { color: #63b3ed; }
.log-entry.log-debug .log-level { color: #a0aec0; }
.log-message { color: #cbd5e0; word-break: break-all; flex: 1; }
.no-logs { padding: 16px 12px; color: #4a5568; font-size: 0.82rem; text-align: center; }
/* ---- module grouping ---- */
.module-heading {
  display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
  margin: 28px 0 10px; padding-bottom: 8px; border-bottom: 1px solid #2d3748;
}
.module-heading:first-of-type { margin-top: 4px; }
.module-heading h2 { font-size: 1rem; color: #e2e8f0; margin: 0; }
.make-chip, .test-make-chip {
  font-family: 'Courier New', monospace; font-size: 0.72rem; color: #a0aec0;
  background: #0f1117; border: 1px solid #2d3748; border-radius: 6px;
  padding: 2px 8px; flex-shrink: 0; white-space: nowrap;
}
.module-counts { margin-left: auto; font-size: 0.8rem; color: #718096; }
/* ---- screenshot ---- */
.screenshot-section { margin-bottom: 12px; }
.screenshot-section summary {
  cursor: pointer; font-size: 0.8rem; color: #718096; padding: 6px 0;
  user-select: none; list-style: none; display: flex; align-items: center; gap: 6px;
}
.screenshot-section summary::before { content: "▶"; font-size: 0.65rem; transition: transform .2s; }
.screenshot-section[open] summary::before { transform: rotate(90deg); }
.screenshot-section img {
  max-width: 100%; border-radius: 6px; border: 1px solid #2d3748;
  margin-top: 8px; display: block;
}
"""

_JS = r"""
function toggleLogs(header) {
  const body = header.nextElementSibling;
  const chevron = header.querySelector('.chevron');
  const isOpen = body.style.display !== 'none';
  body.style.display = isOpen ? 'none' : 'block';
  chevron.classList.toggle('open', !isOpen);
}

function filterTests(status, btn) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.test-card').forEach(card => {
    card.style.display = (status === 'all' || card.dataset.status === status) ? '' : 'none';
  });
}

function searchTests(query) {
  const q = query.toLowerCase();
  document.querySelectorAll('.test-card').forEach(card => {
    const name = card.querySelector('.test-name').textContent.toLowerCase();
    const nodeId = card.querySelector('.test-module').textContent.toLowerCase();
    card.style.display = (name.includes(q) || nodeId.includes(q)) ? '' : 'none';
  });
}

function toggleLevel(btn, level) {
  const entries = btn.closest('.logs-section').querySelectorAll('.log-entry');
  const active = btn.classList.toggle('active-' + level);
  entries.forEach(e => {
    if (e.dataset.level === level) e.style.display = active ? '' : 'none';
  });
}
"""


def _level_class(log_type: str) -> str:
    t = log_type.lower()
    if t in ("error", "pageerror"):
        return "log-error"
    if t in ("warning", "warn"):
        return "log-warn"
    if t == "info":
        return "log-info"
    return "log-debug"


def _build_log_entries(logs: list) -> str:
    if not logs:
        return '<div class="no-logs">No browser console logs captured for this test.</div>'
    parts = []
    for entry in logs:
        level = entry["type"].lower()
        cls = _level_class(entry["type"])
        parts.append(
            f'<div class="log-entry {cls}" data-level="{escape(level)}">'
            f'<span class="log-time">{escape(entry["time"])}</span>'
            f'<span class="log-level">{escape(entry["type"].upper())}</span>'
            f'<span class="log-message">{escape(entry["message"])}</span>'
            f"</div>"
        )
    return "".join(parts)


def _build_screenshot_html(screenshot_b64: str) -> str:
    if not screenshot_b64:
        return ""
    return (
        '<details class="screenshot-section">'
        "<summary>Screenshot</summary>"
        f'<img src="data:image/png;base64,{screenshot_b64}" alt="test screenshot">'
        "</details>"
    )


_STATUS_LABEL = {"xfailed": "XFAIL", "xpassed": "XPASS"}


def _build_card(result: dict, logs: list) -> str:
    status = result["status"]
    css_class = {
        "passed": "pass", "failed": "fail", "skipped": "skip",
        "xfailed": "xfail", "xpassed": "xpass",
    }.get(status, "skip")

    error_html = ""
    if result.get("error"):
        error_html = f'<div class="error-msg"><pre>{escape(result["error"])}</pre></div>'

    screenshot_html = _build_screenshot_html(result.get("screenshot_b64", ""))
    log_entries_html = _build_log_entries(logs)

    make_target = result.get("make_target", "")
    make_chip_html = f'<span class="test-make-chip">make {escape(make_target)}</span>' if make_target else ""

    return (
        f'<div class="test-card {css_class}" data-status="{escape(status)}">'
        f'<div class="test-header" onclick="toggleLogs(this)">'
        f'<span class="status-badge {css_class}">{_STATUS_LABEL.get(status, status.upper())}</span>'
        f'<span class="test-name">{escape(result["name"])}</span>'
        f'<span class="test-duration">{escape(result.get("duration", ""))}</span>'
        f"{make_chip_html}"
        f'<span class="chevron">&#9660;</span>'
        f"</div>"
        f'<div class="test-body" style="display:none">'
        f'<div class="test-module">{escape(result["node_id"])}</div>'
        f"{error_html}"
        f"{screenshot_html}"
        f'<div class="logs-section">'
        f'<div class="logs-header">'
        f'<span class="logs-title">Browser Console Logs ({len(logs)})</span>'
        f'<div class="log-level-filters">'
        f'<button class="log-filter-btn active-error" onclick="toggleLevel(this,\'error\')">ERROR</button>'
        f'<button class="log-filter-btn active-warn"  onclick="toggleLevel(this,\'warn\')">WARN</button>'
        f'<button class="log-filter-btn active-info"  onclick="toggleLevel(this,\'info\')">INFO</button>'
        f'<button class="log-filter-btn active-log"   onclick="toggleLevel(this,\'log\')">LOG</button>'
        f"</div></div>"
        f'<div class="log-entries">{log_entries_html}</div>'
        f"</div></div></div>"
    )


def generate_log_report(
    results: list,
    log_collector: "LogCollector",
    output_path: str = "log-report.html",
) -> str:
    """
    Generate a self-contained interactive HTML log report.

    Args:
        results:       List of dicts with keys node_id, name, status, duration, error.
        log_collector: LogCollector instance populated during the test run.
        output_path:   Destination file path for the HTML report.

    Returns:
        The resolved output path string.
    """
    passed  = sum(1 for r in results if r["status"] == "passed")
    failed  = sum(1 for r in results if r["status"] == "failed")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    xfailed = sum(1 for r in results if r["status"] == "xfailed")
    xpassed = sum(1 for r in results if r["status"] == "xpassed")
    total   = len(results)

    # Group by feature (same convention as the BDD/email reports) so the run
    # reads as one section per `make` command instead of pytest collection order.
    order: list = []
    groups: dict = {}
    for r in results:
        g = (r.get("feature") or "").strip() or "Tests"
        if g not in groups:
            groups[g] = []
            order.append(g)
        groups[g].append(r)

    sections = []
    for g in order:
        rows = groups[g]
        g_passed = sum(1 for r in rows if r["status"] in ("passed", "xpassed"))
        group_target = next((r.get("make_group") for r in rows if r.get("make_group")), "")
        chip_html = f'<span class="make-chip">make {escape(group_target)}</span>' if group_target else ""
        cards = "".join(_build_card(r, log_collector.get(r["node_id"])) for r in rows)
        sections.append(
            f'<div class="module-heading"><h2>{escape(g)}</h2>{chip_html}'
            f'<span class="module-counts">{g_passed}/{len(rows)} passed</span></div>'
            f"{cards}"
        )
    cards_html = "".join(sections)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f"<title>Log JS Report — Automation Saathi</title>\n"
        f"<style>{_CSS}</style>\n"
        "</head>\n"
        "<body>\n"
        '<div class="header">\n'
        f'  <h1>Automation <span>Saathi</span> — Log JS Report</h1>\n'
        f'  <div class="meta">Generated: {escape(timestamp)}&nbsp;&nbsp;|&nbsp;&nbsp;{total} test(s)</div>\n'
        "</div>\n"
        '<div class="container">\n'
        '  <div class="summary">\n'
        f'    <div class="card total"><div class="count">{total}</div><div class="label">Total</div></div>\n'
        f'    <div class="card passed"><div class="count">{passed}</div><div class="label">Passed</div></div>\n'
        f'    <div class="card failed"><div class="count">{failed}</div><div class="label">Failed</div></div>\n'
        f'    <div class="card skipped"><div class="count">{skipped}</div><div class="label">Skipped</div></div>\n'
        f'    <div class="card xfailed"><div class="count">{xfailed}</div><div class="label">XFail (known bug)</div></div>\n'
        f'    <div class="card xpassed"><div class="count">{xpassed}</div><div class="label">XPass (bug fixed?)</div></div>\n'
        "  </div>\n"
        '  <div class="filters">\n'
        "    <label>Filter:</label>\n"
        f'    <button class="filter-btn active all"  onclick="filterTests(\'all\', this)">All ({total})</button>\n'
        f'    <button class="filter-btn pass"        onclick="filterTests(\'passed\', this)">Passed ({passed})</button>\n'
        f'    <button class="filter-btn fail"        onclick="filterTests(\'failed\', this)">Failed ({failed})</button>\n'
        f'    <button class="filter-btn skip"        onclick="filterTests(\'skipped\', this)">Skipped ({skipped})</button>\n'
        f'    <button class="filter-btn xfail"       onclick="filterTests(\'xfailed\', this)">XFail ({xfailed})</button>\n'
        f'    <button class="filter-btn xpass"       onclick="filterTests(\'xpassed\', this)">XPass ({xpassed})</button>\n'
        '    <div class="search-box">\n'
        '      <input type="text" id="searchInput" placeholder="Search tests…" oninput="searchTests(this.value)">\n'
        "    </div>\n"
        "  </div>\n"
        f'  <div id="test-list">{cards_html}</div>\n'
        "</div>\n"
        f"<script>{_JS}</script>\n"
        "</body>\n"
        "</html>\n"
    )

    Path(output_path).write_text(html, encoding="utf-8")
    return str(Path(output_path).resolve())
