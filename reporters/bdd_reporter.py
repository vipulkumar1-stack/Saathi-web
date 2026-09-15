"""Plain-English, Cucumber-style HTML summary report.

Built from the per-test results collected in conftest (description, curated
steps, expected outcome, and a one-line failure reason) — NOT stack traces. It
answers four things at a glance:
  * a summary of every test run,
  * a jump-list straight to whatever failed,
  * every scenario, grouped by feature — and next to each feature (and each
    scenario) the exact `make <target>` that reruns just it, and
  * for failed tests, WHY it failed in plain English (plus the screenshot).

Self-contained single HTML (inline CSS, embedded screenshots) — opens in any
browser with no server or Java, unlike the Allure report.
"""
import re
from html import escape
from pathlib import Path

_STATUS = {
    "passed":  ("Passed",  "#1a7f37", "#e9f7ee", "✓"),
    "failed":  ("Failed",  "#d1242f", "#fdeaea", "✗"),
    "skipped": ("Skipped", "#9a6700", "#fdf6e3", "•"),
    # known_bug tests: xfailed = failed as expected (benign), xpassed = the
    # documented bug unexpectedly passed (the app fix may have landed).
    "xfailed": ("Known bug (XFAIL)",   "#8250df", "#f5f0ff", "x"),
    "xpassed": ("Bug fixed? (XPASS)",  "#bf3989", "#fff0f7", "!"),
}


def _humanize_name(name: str) -> str:
    n = re.sub(r"^test_", "", name or "").replace("_", " ").strip()
    return (n[:1].upper() + n[1:]) if n else (name or "Scenario")


def _steps_list(steps: str) -> list[str]:
    """Split the curated steps blob into individual plain-English lines,
    stripping any leading '1. ' numbering (we re-number in the template)."""
    out = []
    for line in (steps or "").splitlines():
        line = line.strip()
        if line:
            out.append(re.sub(r"^\d+[.)]\s*", "", line))
    return out


def _plain_reason(actual: str, error: str) -> str:
    """Turn a pytest/Playwright failure into a one-line, plain-English reason."""
    text = (actual or "").strip()
    blob = (text + " " + (error or "")).lower()

    if "timeout" in blob or "timed out" in blob:
        m = re.search(r"waiting for (.+?)(?:\s+to be| to have| to contain|$)", text, re.I)
        target = (m.group(1).strip() if m else "")
        if target:
            return f"Timed out waiting for {target[:130]} — the expected element or state never appeared."
        return "The step timed out — the expected element or page state never appeared."
    if "url" in blob and ("expected" in blob or "to_have_url" in blob or "not_to_have_url" in blob):
        return "The page did not end up on the expected URL (navigation didn't happen as expected)."
    if "element(s) not found" in blob or "to be visible" in blob or "not visible" in blob:
        return "An element that should have been visible was not found on the page."
    if "to be hidden" in blob:
        return "An element that should have been hidden was still visible."
    if "to be enabled" in blob or "to be disabled" in blob:
        return f"A control was in the wrong enabled/disabled state. ({text[:120]})"
    if "to have count" in blob or "to_have_count" in blob:
        return f"The number of matching items didn't match what was expected. ({text[:120]})"
    if text:
        return text[:220]
    return "The test failed. Open the Allure report (make open-report) for the full technical trace."


def _summary(results: list[dict]):
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "passed")
    failed = sum(1 for r in results if r.get("status") == "failed")
    skipped = sum(1 for r in results if r.get("status") == "skipped")
    xfailed = sum(1 for r in results if r.get("status") == "xfailed")
    xpassed = sum(1 for r in results if r.get("status") == "xpassed")
    secs = 0.0
    for r in results:
        try:
            secs += float(str(r.get("duration", "0")).rstrip("s"))
        except ValueError:
            pass
    # An XPASS did pass — excluding it from the numerator would make a run
    # that just fixed a documented bug look like it regressed. xfailed stays
    # out: it legitimately failed, just an expected/benign one.
    rate = f"{((passed + xpassed) / total * 100):.0f}%" if total else "—"
    return total, passed, failed, skipped, xfailed, xpassed, rate, secs


def _duration_seconds(rows: list[dict]) -> float:
    secs = 0.0
    for r in rows:
        try:
            secs += float(str(r.get("duration", "0")).rstrip("s"))
        except ValueError:
            pass
    return secs


def _anchor_id(r: dict) -> str:
    raw = r.get("node_id") or r.get("name") or "scenario"
    return "t-" + re.sub(r"[^A-Za-z0-9_-]+", "-", raw).strip("-")


def _make_chip(target: str, label: str = "make") -> str:
    if not target:
        return ""
    return (f'<code style="font-size:11px;color:#57606a;background:#f6f8fa;'
            f'border:1px solid #d0d7de;border-radius:6px;padding:2px 8px;white-space:nowrap">'
            f'{escape(label)} {escape(target)}</code>')


def _group_label(r: dict) -> str:
    return (r.get("feature") or "").strip() or "Tests"


def _scenario_html(r: dict, compact: bool) -> str:
    label, color, bg, icon = _STATUS.get(r.get("status", ""), _STATUS["skipped"])
    title = r.get("description") or _humanize_name(r.get("name", ""))
    steps = _steps_list(r.get("steps", ""))
    steps_html = "".join(f"<li>{escape(s)}</li>" for s in steps) or "<li><em>No steps recorded.</em></li>"
    expected = r.get("expected_outcome", "")
    anchor = _anchor_id(r)
    chip = _make_chip(r.get("make_target", ""))

    exp_html = (f'<div style="margin-top:8px;color:#57606a;font-size:13px"><b>Expected:</b> {escape(expected)}</div>'
                if expected else "")

    if compact:
        # Passed/skipped: a one-line summary that still expands to the steps
        # + expected outcome, and the make target to rerun just this test.
        return f"""
        <details id="{anchor}" style="border:1px solid #d0d7de;border-radius:8px;padding:0;margin:6px 0;background:#fff">
          <summary style="list-style:none;cursor:pointer;padding:9px 14px;display:flex;align-items:center;gap:10px">
            <span style="flex:0 0 auto;width:20px;height:20px;border-radius:50%;background:{bg};color:{color};
                  display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:11px">{icon}</span>
            <span style="font-size:13.5px">{escape(title)}</span>
            <span style="font-size:11px;color:#8c959f">{escape(str(r.get('duration','')))}</span>
            <span style="margin-left:auto">{chip}</span>
          </summary>
          <div style="padding:0 14px 12px 44px">
            <div style="font-weight:600;color:#57606a;font-size:11px;text-transform:uppercase;letter-spacing:.04em">Steps</div>
            <ol style="margin:6px 0 0;padding-left:20px;line-height:1.7;font-size:13px">{steps_html}</ol>
            {exp_html}
          </div>
        </details>"""

    reason_html = ""
    if r.get("status") == "failed":
        reason = _plain_reason(r.get("actual_outcome", ""), r.get("error", ""))
        shot = r.get("screenshot_b64", "")
        img = (f'<details style="margin-top:8px"><summary style="cursor:pointer;color:#57606a">'
               f'View screenshot at failure</summary>'
               f'<img src="data:image/png;base64,{shot}" style="max-width:100%;border:1px solid #d0d7de;'
               f'border-radius:8px;margin-top:8px"/></details>') if shot else ""
        reason_html = (
            f'<div style="margin-top:10px;padding:10px 12px;background:#fdeaea;border-left:4px solid #d1242f;'
            f'border-radius:6px"><b style="color:#d1242f">Why it failed:</b> {escape(reason)}{img}</div>'
        )
    elif r.get("status") == "xpassed":
        reason_html = (
            '<div style="margin-top:10px;padding:10px 12px;background:#fff0f7;border-left:4px solid #bf3989;'
            'border-radius:6px"><b style="color:#bf3989">Unexpected pass:</b> this documented bug now behaves '
            'correctly. Remove <code>@pytest.mark.xfail(strict=True)</code> so the test guards the fix.</div>'
        )

    return f"""
    <div id="{anchor}" style="border:1px solid #d0d7de;border-radius:10px;padding:14px 16px;margin:10px 0;background:#fff">
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
        <span style="flex:0 0 auto;width:26px;height:26px;border-radius:50%;background:{bg};color:{color};
              display:inline-flex;align-items:center;justify-content:center;font-weight:700">{icon}</span>
        <span style="font-weight:600;font-size:15px">{escape(title)}</span>
        <span style="margin-left:auto;font-size:12px;font-weight:700;color:{color}">{label}</span>
        <span style="font-size:12px;color:#8c959f">{escape(str(r.get('duration','')))}</span>
      </div>
      <div style="margin-top:10px;color:#1f2328;font-size:14px">
        <div style="font-weight:600;color:#57606a;font-size:12px;text-transform:uppercase;letter-spacing:.04em">Steps</div>
        <ol style="margin:6px 0 0;padding-left:20px;line-height:1.7">{steps_html}</ol>
      </div>
      {exp_html}
      {reason_html}
      {f'<div style="margin-top:10px">{chip}</div>' if chip else ""}
    </div>"""


def _failure_index_html(failures: list[dict]) -> str:
    items = "".join(
        f'<li style="margin-bottom:2px"><a href="#{_anchor_id(r)}" style="color:#d1242f;text-decoration:none">'
        f'{escape(r.get("description") or _humanize_name(r.get("name","")))}</a>'
        f' <span style="color:#8c959f">· {escape(_group_label(r))}</span></li>'
        for r in failures
    )
    return (
        f'<div style="margin:20px 0;padding:14px 16px;background:#fdeaea;border:1px solid #f3c2c2;'
        f'border-radius:8px"><div style="font-weight:700;color:#d1242f;margin-bottom:6px">'
        f'{len(failures)} test{"s" if len(failures) != 1 else ""} failed — jump to:</div>'
        f'<ul style="margin:0;padding-left:20px;line-height:1.8;font-size:13px">{items}</ul></div>'
    )


def _section_html(feature: str, rows: list[dict]) -> str:
    total = len(rows)
    passed = sum(1 for r in rows if r.get("status") == "passed")
    failed = sum(1 for r in rows if r.get("status") == "failed")
    skipped = sum(1 for r in rows if r.get("status") == "skipped")
    xfailed = sum(1 for r in rows if r.get("status") == "xfailed")
    xpassed = sum(1 for r in rows if r.get("status") == "xpassed")

    # The Makefile's file-level target, when the whole file maps to one
    # (test_17's two classes each have their own group instead — every row
    # in a group carries the same make_group, so the first non-empty one wins).
    group_target = next((r.get("make_group") for r in rows if r.get("make_group")), "")
    chip = _make_chip(group_target)

    counts = f"{passed} passed"
    if failed:
        counts += f' · <span style="color:#d1242f">{failed} failed</span>'
    if xpassed:
        counts += f' · <span style="color:#bf3989">{xpassed} XPASS</span>'
    if skipped:
        counts += f' · <span style="color:#9a6700">{skipped} skipped</span>'
    if xfailed:
        counts += f' · <span style="color:#8250df">{xfailed} known bug</span>'

    order_key = {"failed": 0, "xpassed": 1, "skipped": 2, "xfailed": 3, "passed": 4}
    ordered = sorted(rows, key=lambda r: order_key.get(r.get("status", ""), 5))
    rows_html = "".join(_scenario_html(r, compact=(r.get("status") not in ("failed", "xpassed"))) for r in ordered)

    return f"""
    <section style="margin:26px 0">
      <div style="display:flex;align-items:center;flex-wrap:wrap;gap:10px;padding-bottom:8px;border-bottom:2px solid #d0d7de">
        <h2 style="margin:0;font-size:17px">{escape(feature)}</h2>
        {chip}
        <span style="margin-left:auto;font-size:13px;color:#57606a">{counts} · {total} total · {_duration_seconds(rows):.0f}s</span>
      </div>
      {rows_html}
    </section>"""


def generate_bdd_report(test_results: list[dict], output_file: str = "test-summary.html") -> str:
    total, passed, failed, skipped, xfailed, xpassed, rate, secs = _summary(test_results)

    def card(labeltxt, value, color):
        return (f'<div style="flex:1;min-width:120px;background:#fff;border:1px solid #d0d7de;border-radius:10px;'
                f'padding:14px 16px"><div style="color:#57606a;font-size:13px">{labeltxt}</div>'
                f'<div style="font-size:28px;font-weight:700;color:{color}">{value}</div></div>')

    cards = "".join([
        card("Total", total, "#1f2328"),
        card("Passed", passed, "#1a7f37"),
        card("Failed", failed, "#d1242f"),
        card("Skipped", skipped, "#9a6700"),
        card("Known bug (XFAIL)", xfailed, "#8250df"),
        card("XPASS — bug fixed?", xpassed, "#bf3989"),
        card("Pass rate", rate, "#1f2328"),
        card("Duration", f"{secs:.0f}s", "#1f2328"),
    ])

    # A jump-list straight to what failed — kept, on top of the full grouped
    # listing below, so the reader isn't stuck scrolling to find failures.
    failures = [r for r in test_results if r.get("status") == "failed"]
    xpasses = [r for r in test_results if r.get("status") == "xpassed"]
    if failures:
        top_banner = _failure_index_html(failures)
    elif xpasses:
        # No regressions, but a strict xfail unexpectedly passed — the "all
        # green" banner below would be misleading here: the run still exits
        # non-zero and something needs attention (removing the xfail marker).
        items = "".join(
            f'<li style="margin-bottom:2px"><a href="#{_anchor_id(r)}" style="color:#bf3989;text-decoration:none">'
            f'{escape(r.get("description") or _humanize_name(r.get("name","")))}</a>'
            f' <span style="color:#8c959f">· {escape(_group_label(r))}</span></li>'
            for r in xpasses
        )
        top_banner = (
            f'<div style="margin:20px 0;padding:14px 16px;background:#fff0f7;border:1px solid #f3b8d8;'
            f'border-radius:8px"><div style="font-weight:700;color:#bf3989;margin-bottom:6px">'
            f'{len(xpasses)} known-bug test{"s" if len(xpasses) != 1 else ""} unexpectedly passed — '
            f'remove the xfail marker:</div>'
            f'<ul style="margin:0;padding-left:20px;line-height:1.8;font-size:13px">{items}</ul></div>'
        )
    else:
        top_banner = (
            '<div style="margin:20px 0;padding:14px 16px;background:#e9f7ee;border:1px solid #1a7f37;'
            'border-radius:8px;color:#1a7f37;font-weight:600">All tests passed — no failures to report. 🎉'
            '</div>'
        )

    # Every test, grouped by feature (module), in first-seen order — same
    # grouping convention as the email report's per-module breakdown.
    order, groups = [], {}
    for r in test_results:
        g = _group_label(r)
        if g not in groups:
            groups[g] = []
            order.append(g)
        groups[g].append(r)

    sections_html = "".join(_section_html(g, groups[g]) for g in order)

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Saathi Automation — Test Report</title></head>
<body style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:#f6f8fa;
             color:#1f2328;margin:0;padding:24px">
  <div style="max-width:960px;margin:0 auto">
    <h1 style="margin:0 0 4px">Saathi Automation — Test Report</h1>
    <p style="margin:0 0 18px;color:#57606a">Plain-English summary of the latest run, grouped by feature —
      each section and each test shows the <code>make</code> command that reruns just it.</p>
    <div style="display:flex;gap:12px;flex-wrap:wrap">{cards}</div>
    {top_banner}
    {sections_html}
    <p style="margin:26px 0;color:#8c959f;font-size:12px">
      For the full step-by-step timeline, browser logs, and raw stack traces,
      open the Allure report (<code>make allure-report</code>).</p>
  </div>
</body></html>"""

    path = Path(output_file)
    path.write_text(html, encoding="utf-8")
    return str(path)
