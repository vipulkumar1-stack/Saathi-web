"""Email the generated pytest reports after a run.

Configuration is read from environment variables (loaded from .env by
python-dotenv, same as the rest of the framework). Nothing is hardcoded so no
credentials live in source.

Required env vars:
    REPORT_EMAIL_TO        comma-separated recipient address(es)
    REPORT_EMAIL_USER      the sending Gmail / Workspace account
    REPORT_EMAIL_PASSWORD  a 16-char Google App Password (NOT the login password)

Optional env vars:
    REPORT_EMAIL_FROM      From address (defaults to REPORT_EMAIL_USER)
    REPORT_EMAIL_HOST      SMTP host   (default smtp.gmail.com)
    REPORT_EMAIL_PORT      SMTP port   (default 587, STARTTLS)
"""
import os
import re
import io
import zipfile
import smtplib
import mimetypes
import html as _html
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

_STATUS_COLOR = {
    "passed": "#1a7f37", "failed": "#d1242f", "skipped": "#9a6700",
    "xfailed": "#8250df", "xpassed": "#bf3989",
}
# Short labels for the Status column — status.upper() alone would print
# "XFAILED"/"XPASSED", which is needlessly long next to PASSED/FAILED.
_STATUS_LABEL = {"xfailed": "XFAIL", "xpassed": "XPASS"}


def _module_of(r: dict) -> str:
    """Group label for a result: the allure feature if set, else the test file
    stem parsed from the node id (e.g. tests/test_09_mark_as_lost.py -> test_09_mark_as_lost)."""
    feat = (r.get("feature") or "").strip()
    if feat:
        return feat
    nid = r.get("node_id") or ""
    stem = nid.split("::")[0].split("/")[-1]
    return stem[:-3] if stem.endswith(".py") else (stem or "tests")


# `make` targets that generate/open a report rather than run tests — never a
# meaningful "what ran" label even though they can appear in MAKECMDGOALS
# alongside (or instead of) a real test target, e.g. `make report`.
_NON_RUN_GOALS = {"reports", "report", "report-email", "allure-report",
                  "generate-report", "open-report", "open-reports",
                  "open-log-report", "open-excel-report", "check-email",
                  "check-targets", "clean", "install", "reset-session", "help"}


def _run_scope(test_results: list[dict]) -> str:
    """Short label for WHAT ran, for the subject line — so a single-test email
    and a full-suite email are distinguishable in an inbox. Prefers the make
    target (set by the Makefile's `export MAKECMDGOALS`); falls back to the
    result rows themselves so a bare `pytest` invocation (no make) still gets
    a correct label."""
    goals = [g for g in os.getenv("MAKECMDGOALS", "").split() if g not in _NON_RUN_GOALS]
    if len(goals) == 1:
        return "full suite" if goals[0] == "all" else f"make {goals[0]}"
    if len(goals) > 1:
        return f"make {' + '.join(goals)}"
    modules = list(dict.fromkeys(_module_of(r) for r in test_results))
    if len(modules) == 1:
        return modules[0]
    if modules:
        return f"{len(modules)} features / {len(test_results)} tests"
    return "run"


def _summarise(test_results: list[dict]) -> tuple[str, int, int, int, int, int, int]:
    total = len(test_results)
    passed = sum(1 for r in test_results if r.get("status") == "passed")
    failed = sum(1 for r in test_results if r.get("status") == "failed")
    skipped = sum(1 for r in test_results if r.get("status") == "skipped")
    xfailed = sum(1 for r in test_results if r.get("status") == "xfailed")
    xpassed = sum(1 for r in test_results if r.get("status") == "xpassed")
    scope = _run_scope(test_results)
    subject = f"Saathi Automation Report — {scope} — {passed}/{total} passed, {failed} failed"
    if xfailed:
        subject += f", {xfailed} xfail"
    if xpassed:
        subject += f", {xpassed} XPASS (bug fixed?)"
    return subject, total, passed, failed, skipped, xfailed, xpassed


ALLURE_ATTACHMENT = "allure-report.html"
SUMMARY_ATTACHMENT = "test-summary.html"


def _attached_reports(summary_attached: bool, allure_attached: bool) -> list[str]:
    reports = []
    if summary_attached:
        reports.append("Plain-English summary (test-summary.html) — failed tests, in simple English")
    reports.append("Excel summary (test-report.xlsx)")
    if allure_attached:
        reports.append("Full Allure report (inside reports.zip) — unzip, then open the .html "
                        "in any browser for the interactive report")
    return reports


def _steps_lines(steps: str) -> list[str]:
    """Split a curated TEST_STEPS blob into individual lines, stripping any
    leading '1. ' numbering (re-numbered by each renderer)."""
    out = []
    for line in (steps or "").splitlines():
        line = line.strip()
        if line:
            out.append(re.sub(r"^\d+[.)]\s*", "", line))
    return out


def _body(total: int, passed: int, failed: int, skipped: int, xfailed: int, xpassed: int,
          test_results: list[dict], allure_attached: bool = False,
          summary_attached: bool = False) -> str:
    lines = [
        "Automated pytest run finished.",
        "",
        f"  Total:   {total}",
        f"  Passed:  {passed}",
        f"  Failed:  {failed}",
        f"  Skipped: {skipped}",
        f"  Known bug (xfail): {xfailed}",
        f"  Unexpected pass (XPASS): {xpassed}",
        "",
    ]
    failures = [r for r in test_results if r.get("status") == "failed"]
    if failures:
        lines.append("Failed tests:")
        for r in failures:
            reason = (r.get("actual_outcome") or "").strip()
            lines.append(f"  - {r.get('name', r.get('node_id', '?'))}"
                         + (f"  ({reason})" if reason else ""))
            for i, step in enumerate(_steps_lines(r.get("steps", "")), 1):
                lines.append(f"      {i}. {step}")
            make_target = (r.get("make_target") or "").strip()
            if make_target:
                lines.append(f"      Rerun: make {make_target}")
        lines.append("")
    xpasses = [r for r in test_results if r.get("status") == "xpassed"]
    if xpasses:
        lines.append("Known bugs that now PASS (remove the xfail marker):")
        for r in xpasses:
            lines.append(f"  - {r.get('name', r.get('node_id', '?'))}  ({r.get('node_id', '')})")
        lines.append("")
    lines.append("Attached reports:")
    lines += [f"  - {r}" for r in _attached_reports(summary_attached, allure_attached)]
    return "\n".join(lines)


def _html_body(total: int, passed: int, failed: int, skipped: int, xfailed: int, xpassed: int,
               test_results: list[dict], allure_attached: bool = False,
               summary_attached: bool = False) -> str:
    """A self-rendering HTML summary shown directly in the inbox (Gmail strips
    <script>, so this is a static, inline-styled table — no JS needed). This body
    IS the summary report; recipients don't need to open an attachment for it."""
    def cell(txt, **style):
        st = ";".join(f"{k.replace('_','-')}:{v}" for k, v in style.items())
        return f'<td style="padding:6px 10px;border-bottom:1px solid #eee;{st}">{_html.escape(str(txt))}</td>'

    # An XPASS did pass — excluding it would make a run that just fixed a
    # documented bug look like it regressed. xfailed stays out: it legitimately
    # failed, just an expected/benign one.
    pass_rate = f"{((passed + xpassed) / total * 100):.0f}%" if total else "—"
    generated = datetime.now().strftime("%d %b %Y, %H:%M")

    # Failures-first callout: the one thing a reader needs immediately.
    failures = [r for r in test_results if r.get("status") == "failed"]
    fail_block = ""
    if failures:
        def failure_item(r):
            steps = _steps_lines(r.get("steps", ""))
            steps_html = (
                '<ol style="margin:6px 0 0;padding-left:18px;color:#444;font-size:13px">'
                + "".join(f"<li>{_html.escape(s)}</li>" for s in steps)
                + "</ol>"
            ) if steps else ""
            make_target = (r.get("make_target") or "").strip()
            rerun_html = (
                f'<div style="margin-top:4px;font-size:13px;color:#444">'
                f'Rerun: <code style="background:#f0f0f0;padding:1px 4px;border-radius:3px">'
                f'make {_html.escape(make_target)}</code></div>'
            ) if make_target else ""
            return (
                "<li style='margin-bottom:10px'>"
                f"<b>{_html.escape(r.get('name') or r.get('node_id') or '?')}</b>"
                f" <span style='color:#888'>· {_html.escape(_module_of(r))}</span>"
                + (f"<br><span style='color:#8a1f1f'>{_html.escape((r.get('actual_outcome') or '').strip())}</span>"
                   if (r.get('actual_outcome') or '').strip() else "")
                + steps_html + rerun_html
                + "</li>"
            )
        items = "".join(failure_item(r) for r in failures)
        fail_block = (
            '<div style="margin:0 0 20px;padding:12px 16px;background:#fff5f5;'
            'border:1px solid #f3c2c2;border-left:4px solid #d1242f;border-radius:4px">'
            f'<div style="font-weight:700;color:#d1242f;margin-bottom:8px">⚠ {len(failures)} failed test(s)</div>'
            f'<ul style="margin:0;padding-left:18px;font-size:14px;color:#1a1a1a">{items}</ul>'
            '</div>'
        )

    # A strict xfail unexpectedly passed — the app bug it documents may be
    # fixed. Not a regression, but not silent either: the marker is now a lie
    # and the run still exits non-zero because of it.
    xpasses = [r for r in test_results if r.get("status") == "xpassed"]
    xpass_block = ""
    if xpasses:
        xpass_items = "".join(
            "<li style='margin-bottom:6px'>"
            f"<b>{_html.escape(r.get('name') or r.get('node_id') or '?')}</b>"
            f" <span style='color:#888'>· {_html.escape(_module_of(r))}</span>"
            "<br><span style='color:#8a2a5c'>remove <code>@pytest.mark.xfail(strict=True)</code></span>"
            "</li>"
            for r in xpasses
        )
        xpass_block = (
            '<div style="margin:0 0 20px;padding:12px 16px;background:#fff0f7;'
            'border:1px solid #f3b8d8;border-left:4px solid #bf3989;border-radius:4px">'
            f'<div style="font-weight:700;color:#bf3989;margin-bottom:8px">'
            f'🎉 {len(xpasses)} known-bug test(s) unexpectedly passed — bug(s) may be fixed</div>'
            f'<ul style="margin:0;padding-left:18px;font-size:14px;color:#1a1a1a">{xpass_items}</ul>'
            '</div>'
        )

    # Detail table grouped by module: a spanning subheader per module, then its
    # tests. Groups preserve first-seen order; within a group, failures/XPASS float up.
    order, groups = [], {}
    for r in test_results:
        m = _module_of(r)
        if m not in groups:
            groups[m] = []
            order.append(m)
        groups[m].append(r)

    _row_order = {"failed": 0, "xpassed": 1, "skipped": 2, "xfailed": 3, "passed": 4}
    body_rows = []
    for m in order:
        members = sorted(groups[m], key=lambda r: _row_order.get(r.get("status", ""), 5))
        g_pass = sum(1 for r in members if r.get("status") in ("passed", "xpassed"))
        body_rows.append(
            f'<tr><td colspan="4" style="padding:10px 10px 4px;font-weight:700;'
            f'background:#f0f3f6;border-top:1px solid #ddd">{_html.escape(m)} '
            f'<span style="font-weight:400;color:#666">· {g_pass}/{len(members)} passed</span></td></tr>'
        )
        for r in members:
            status = r.get("status", "")
            color = _STATUS_COLOR.get(status, "#333")
            label = _STATUS_LABEL.get(status, status.upper())
            body_rows.append(
                "<tr>"
                + cell(r.get("name") or r.get("node_id") or "?")
                + f'<td style="padding:6px 10px;border-bottom:1px solid #eee;font-weight:600;color:{color}">{_html.escape(label)}</td>'
                + cell(r.get("duration") or "")
                + cell(r.get("actual_outcome") or "")
                + "</tr>"
            )

    attached_reports = _attached_reports(summary_attached, allure_attached)
    attached_note = ""
    if attached_reports:
        attached_items = "".join(f"<li>{_html.escape(r)}</li>" for r in attached_reports)
        attached_note = (
            '<p style="margin-top:20px;color:#666;font-size:13px"><b>Attached (optional detail):</b></p>'
            f'<ul style="margin:4px 0 0;color:#666;font-size:13px">{attached_items}</ul>'
        )

    return f"""\
<div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;color:#1a1a1a">
  <h2 style="margin:0 0 4px">Saathi Automation Report</h2>
  <p style="margin:0 0 16px;color:#666">Automated pytest run finished · {generated}</p>
  {fail_block}
  {xpass_block}
  <table style="border-collapse:collapse;margin-bottom:20px">
    <tr>
      <td style="padding:8px 16px;background:#f6f8fa;border:1px solid #eee">Total<br><b style="font-size:20px">{total}</b></td>
      <td style="padding:8px 16px;background:#f6f8fa;border:1px solid #eee;color:#1a7f37">Passed<br><b style="font-size:20px">{passed}</b></td>
      <td style="padding:8px 16px;background:#f6f8fa;border:1px solid #eee;color:#d1242f">Failed<br><b style="font-size:20px">{failed}</b></td>
      <td style="padding:8px 16px;background:#f6f8fa;border:1px solid #eee;color:#9a6700">Skipped<br><b style="font-size:20px">{skipped}</b></td>
      <td style="padding:8px 16px;background:#f6f8fa;border:1px solid #eee;color:#8250df">Known bug<br><b style="font-size:20px">{xfailed}</b></td>
      <td style="padding:8px 16px;background:#f6f8fa;border:1px solid #eee;color:#bf3989">XPASS<br><b style="font-size:20px">{xpassed}</b></td>
      <td style="padding:8px 16px;background:#f6f8fa;border:1px solid #eee">Pass rate<br><b style="font-size:20px">{pass_rate}</b></td>
    </tr>
  </table>
  <table style="border-collapse:collapse;width:100%;font-size:14px">
    <tr style="text-align:left;background:#f6f8fa">
      <th style="padding:6px 10px;border-bottom:2px solid #ddd">Test</th>
      <th style="padding:6px 10px;border-bottom:2px solid #ddd">Status</th>
      <th style="padding:6px 10px;border-bottom:2px solid #ddd">Duration</th>
      <th style="padding:6px 10px;border-bottom:2px solid #ddd">Outcome</th>
    </tr>
    {''.join(body_rows)}
  </table>
  {attached_note}
</div>"""


# Gmail rejects messages over ~25 MB; base64-encoding attachments inflates
# their size ~33%, so cap the raw payload (the zip + any non-html attachments)
# well under that.
MAX_ATTACHMENT_MB = 20


def _smtp_settings() -> dict:
    """Read and validate the REPORT_EMAIL_* env vars. Raises RuntimeError
    naming exactly what's missing — used by both send_report_email and
    check_config so the two can never disagree about what "configured" means."""
    to_raw = os.getenv("REPORT_EMAIL_TO", "").strip()
    user = os.getenv("REPORT_EMAIL_USER", "").strip()
    # Google shows App Passwords as 4 space-separated groups ("abcd efgh ...").
    # SMTP wants them with no spaces, so strip all whitespace defensively.
    password = "".join(os.getenv("REPORT_EMAIL_PASSWORD", "").split())

    missing = [name for name, val in (
        ("REPORT_EMAIL_TO", to_raw),
        ("REPORT_EMAIL_USER", user),
        ("REPORT_EMAIL_PASSWORD", password),
    ) if not val]
    if missing:
        raise RuntimeError(f"missing env var(s): {', '.join(missing)}")

    return {
        "recipients": [addr.strip() for addr in to_raw.split(",") if addr.strip()],
        "user": user,
        "password": password,
        "sender": os.getenv("REPORT_EMAIL_FROM", "").strip() or user,
        "host": os.getenv("REPORT_EMAIL_HOST", "smtp.gmail.com").strip(),
        "port": int(os.getenv("REPORT_EMAIL_PORT", "587")),
    }


def check_config() -> None:
    """Validate REPORT_EMAIL_* and confirm the SMTP server accepts the app
    password — WITHOUT sending any mail. Prints its result; raises on failure
    so `make check-email` exits non-zero. Run this after rotating
    REPORT_EMAIL_PASSWORD or REPORT_EMAIL_TO to catch a bad value before the
    next test run silently swallows the send error.

    Standalone entry point (invoked directly by `make check-email`, not through
    conftest/config.config), so it loads .env itself rather than relying on
    another module having done it first."""
    from dotenv import load_dotenv
    load_dotenv()
    cfg = _smtp_settings()
    with smtplib.SMTP(cfg["host"], cfg["port"], timeout=30) as smtp:
        smtp.starttls()
        smtp.login(cfg["user"], cfg["password"])
    print(f"✅ SMTP config OK — {cfg['user']} via {cfg['host']}:{cfg['port']}")
    print(f"   Recipients: {', '.join(cfg['recipients'])}")


def _build_attachments(attachments: list[str]) -> tuple[bytes | None, list[Path], bool, bool]:
    """Zip every .html attachment into one payload (Gmail/webmail preview a raw
    .html attachment as SOURCE, not the rendered page, regardless of
    Content-Type; a .zip can't be previewed that way, so the recipient
    downloads and opens a fully-rendering file — this also compresses the
    largest report). Non-html attachments (the .xlsx) pass through as-is.

    If the zip would push the message over MAX_ATTACHMENT_MB, drop the single
    largest html member (in practice always the Allure report — by far the
    biggest of the three) and re-zip, rather than fail the whole email.
    Returns (zip_bytes_or_None, other_paths, allure_dropped, summary_dropped).
    """
    html_paths, other_paths = [], []
    for path_str in attachments:
        path = Path(path_str)
        if not path.exists():
            continue
        (html_paths if path.suffix.lower() in (".html", ".htm") else other_paths).append(path)

    if not html_paths:
        return None, other_paths, False, False

    def zip_of(paths: list[Path]) -> bytes:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in paths:
                zf.write(path, arcname=path.name)
        return buf.getvalue()

    other_bytes = sum(p.stat().st_size for p in other_paths)
    zip_bytes = zip_of(html_paths)
    dropped_allure = dropped_summary = False

    while (len(zip_bytes) + other_bytes) / (1024 * 1024) > MAX_ATTACHMENT_MB and len(html_paths) > 1:
        largest = max(html_paths, key=lambda p: p.stat().st_size)
        html_paths.remove(largest)
        if largest.name == ALLURE_ATTACHMENT:
            dropped_allure = True
        elif largest.name == SUMMARY_ATTACHMENT:
            dropped_summary = True
        print(f"⚠️  Dropping {largest.name} from reports.zip — attachments too large to email "
              f"(still saved locally at {largest}).")
        zip_bytes = zip_of(html_paths)

    return zip_bytes, other_paths, dropped_allure, dropped_summary


def send_report_email(test_results: list[dict], attachments: list[str]) -> list[str]:
    """Send the run report. Raises on misconfiguration/SMTP errors so the caller
    can log it; never called unless the env is configured."""
    cfg = _smtp_settings()
    recipients, user, password = cfg["recipients"], cfg["user"], cfg["password"]
    sender, host, port = cfg["sender"], cfg["host"], cfg["port"]

    zip_bytes, other_paths, dropped_allure, dropped_summary = _build_attachments(attachments)
    names = {Path(a).name for a in attachments}
    allure_attached = ALLURE_ATTACHMENT in names and not dropped_allure
    summary_attached = SUMMARY_ATTACHMENT in names and not dropped_summary

    subject, total, passed, failed, skipped, xfailed, xpassed = _summarise(test_results)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.set_content(_body(total, passed, failed, skipped, xfailed, xpassed, test_results,
                          allure_attached, summary_attached))
    msg.add_alternative(
        _html_body(total, passed, failed, skipped, xfailed, xpassed, test_results,
                   allure_attached, summary_attached),
        subtype="html",
    )

    if zip_bytes is not None:
        msg.add_attachment(
            zip_bytes,
            maintype="application",
            subtype="zip",
            filename="reports.zip",
        )

    for path in other_paths:
        ctype, _ = mimetypes.guess_type(path.name)
        maintype, subtype = (ctype.split("/", 1) if ctype else ("application", "octet-stream"))
        msg.add_attachment(
            path.read_bytes(),
            maintype=maintype,
            subtype=subtype,
            filename=path.name,
        )

    # Large attachments (e.g. a 12+ MB Allure report) upload slowly; a short
    # timeout aborts mid-send with "Server not connected". Allow ample time.
    with smtplib.SMTP(host, port, timeout=300) as smtp:
        smtp.starttls()
        smtp.login(user, password)
        smtp.send_message(msg)

    return recipients
