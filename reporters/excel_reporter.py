import math
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import (
    Alignment, Border, Font, PatternFill, Side
)
from openpyxl.utils import get_column_letter


# ── Colour palette ────────────────────────────────────────────────────────────
_DARK_BG    = "0F1117"
_HEADER_BG  = "1A1F2E"
_PASS_BG    = "1C3A2A"
_FAIL_BG    = "3A1C1C"
_SKIP_BG    = "3A2E1C"
_XFAIL_BG   = "2D2440"
_XPASS_BG   = "3A1C2E"
_PASS_FG    = "68D391"
_FAIL_FG    = "FC8181"
_SKIP_FG    = "F6AD55"
_XFAIL_FG   = "B794F4"
_XPASS_FG   = "F687B3"
_WHITE      = "E2E8F0"
_MUTED      = "718096"
_ACCENT     = "667EEA"
_BORDER_COL = "2D3748"


def _fill(hex_color: str) -> PatternFill:
    return PatternFill("solid", fgColor=hex_color)


def _font(bold=False, color=_WHITE, size=10) -> Font:
    return Font(bold=bold, color=color, size=size, name="Calibri")


def _thin_border() -> Border:
    side = Side(style="thin", color=_BORDER_COL)
    return Border(left=side, right=side, top=side, bottom=side)


def _center() -> Alignment:
    return Alignment(horizontal="center", vertical="center", wrap_text=True)


def _left() -> Alignment:
    return Alignment(horizontal="left", vertical="center", wrap_text=True)


# ── Results sheet ─────────────────────────────────────────────────────────────

_COLUMNS = [
    ("#",             5),
    ("Test Name",    38),
    ("Module",       28),
    ("Make Command", 26),
    ("Duration",      9),
    ("Description",  42),
    ("Steps",         40),
    ("Status",         9),
    ("Error",         70),
]

# Column index (1-based) for columns that need special treatment
_COL_NUM      = 1
_COL_DURATION = 5
_COL_STATUS   = 8
_COL_ERROR    = 9


def _group_key(r: dict) -> str:
    """Group label for a result: the allure feature if set, else the test
    file stem parsed from the node id — same convention as
    reporters/email_reporter.py's _module_of, so all reports group identically."""
    feat = (r.get("feature") or "").strip()
    if feat:
        return feat
    nid = r.get("node_id") or ""
    stem = nid.split("::")[0].split("/")[-1]
    return stem[:-3] if stem.endswith(".py") else (stem or "tests")


def _duration_seconds(rows: list) -> float:
    secs = 0.0
    for r in rows:
        try:
            secs += float(str(r.get("duration", "0")).rstrip("s"))
        except ValueError:
            pass
    return secs


def _grouped(results: list):
    """Results grouped by feature, first-seen order — the same grouping the
    HTML/email reports use, so all three reports read the same way."""
    order, groups = [], {}
    for r in results:
        g = _group_key(r)
        if g not in groups:
            groups[g] = []
            order.append(g)
        groups[g].append(r)
    return order, groups


def _ordered_results(results: list) -> list:
    """Results sorted by group (first-seen order), failures floated to the
    top within each group — makes the flat Results sheet scan like the
    grouped HTML report instead of the pytest collection order."""
    order, groups = _grouped(results)
    ordered = []
    for g in order:
        ordered.extend(sorted(
            groups[g],
            key=lambda r: {"failed": 0, "xpassed": 1, "skipped": 2, "xfailed": 3, "passed": 4}.get(r.get("status", ""), 5),
        ))
    return ordered


def _write_results(ws, results: list) -> None:
    ws.sheet_view.showGridLines = False

    for col_idx, (header, width) in enumerate(_COLUMNS, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    # Header row
    ws.row_dimensions[1].height = 24
    for col_idx, (header, _) in enumerate(_COLUMNS, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font      = _font(bold=True, color=_ACCENT)
        cell.fill      = _fill(_HEADER_BG)
        cell.alignment = _center()
        cell.border    = _thin_border()

    # Freeze header row
    ws.freeze_panes = "A2"

    status_styles = {
        "passed":  (_PASS_FG, _PASS_BG),
        "failed":  (_FAIL_FG, _FAIL_BG),
        "skipped": (_SKIP_FG, _SKIP_BG),
        "xfailed": (_XFAIL_FG, _XFAIL_BG),
        "xpassed": (_XPASS_FG, _XPASS_BG),
    }
    status_label = {"xfailed": "XFAIL", "xpassed": "XPASS"}

    for row_idx, result in enumerate(results, start=2):
        status  = result["status"]
        fg, bg  = status_styles.get(status, (_WHITE, _DARK_BG))
        row_bg  = _DARK_BG if row_idx % 2 == 0 else _HEADER_BG

        # `actual_outcome` (not the raw `error` traceback) already holds the
        # single most meaningful line pytest_runtest_makereport extracted —
        # the AssertionError/TimeoutError text itself, not the "file:line: in
        # test_name" header that split("\n")[0] on the raw traceback used to
        # keep. The full traceback is still preserved verbatim in
        # log-report.html for deep debugging; this column is for a fast scan.
        # xpassed also gets its outcome text — that IS the actionable "bug
        # looks fixed" signal; xfailed stays blank, it's the benign case.
        error_text = (result.get("actual_outcome") or "").strip() if status in ("failed", "xpassed") else ""

        steps = result.get("steps", "")
        n_step_lines = steps.count("\n") + 1 if steps else 1
        # Error text wraps within the column too (wrap_text=True below) — size
        # the row for whichever is taller so a long assertion message isn't
        # visually clipped under a short Steps cell.
        error_col_width = _COLUMNS[_COL_ERROR - 1][1]
        n_error_lines = math.ceil(len(error_text) / max(1, error_col_width - 2)) if error_text else 1
        n_lines = max(n_step_lines, n_error_lines)
        ws.row_dimensions[row_idx].height = max(20, n_lines * 14 + 6)

        make_target = result.get("make_target", "")

        values = [
            row_idx - 1,
            result["name"],
            result["node_id"].split("::")[0],
            f"make {make_target}" if make_target else "",
            result.get("duration", ""),
            result.get("description", ""),
            steps,
            status_label.get(status, status.upper()),
            error_text,
        ]

        for col_idx, value in enumerate(values, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.border = _thin_border()

            if col_idx == _COL_STATUS:
                cell.font      = _font(bold=True, color=fg)
                cell.fill      = _fill(bg)
                cell.alignment = _center()
            elif col_idx in (_COL_NUM, _COL_DURATION):
                cell.font      = _font(color=_MUTED)
                cell.fill      = _fill(row_bg)
                cell.alignment = _center()
            elif col_idx == _COL_ERROR:
                cell.font      = _font(color=(_XPASS_FG if status == "xpassed" else _FAIL_FG) if error_text else _MUTED)
                cell.fill      = _fill(row_bg)
                cell.alignment = _left()
            else:
                cell.font      = _font(color=_WHITE)
                cell.fill      = _fill(row_bg)
                cell.alignment = _left()

    # Lets a reviewer filter/sort by Module, Make Command, or Status in Excel.
    ws.auto_filter.ref = ws.dimensions


# ── By Command sheet ─────────────────────────────────────────────────────────
# One row per feature, with the `make` command that reruns that whole group —
# the "which command do I rerun?" view, versus the per-test Results sheet.

_CMD_COLUMNS = [
    ("Make Command", 24),
    ("Module",       30),
    ("Total",         8),
    ("Passed",        8),
    ("Failed",        8),
    ("Skipped",       8),
    ("XFail",         8),
    ("XPass",         8),
    ("Pass rate",    10),
    ("Duration",     10),
]


def _write_by_command(ws, results: list) -> None:
    ws.sheet_view.showGridLines = False

    for col_idx, (header, width) in enumerate(_CMD_COLUMNS, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    ws.row_dimensions[1].height = 24
    for col_idx, (header, _) in enumerate(_CMD_COLUMNS, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font      = _font(bold=True, color=_ACCENT)
        cell.fill      = _fill(_HEADER_BG)
        cell.alignment = _center()
        cell.border    = _thin_border()
    ws.freeze_panes = "A2"

    order, groups = _grouped(results)

    for row_idx, group in enumerate(order, start=2):
        rows    = groups[group]
        total   = len(rows)
        passed  = sum(1 for r in rows if r.get("status") == "passed")
        failed  = sum(1 for r in rows if r.get("status") == "failed")
        skipped = sum(1 for r in rows if r.get("status") == "skipped")
        xfailed = sum(1 for r in rows if r.get("status") == "xfailed")
        xpassed = sum(1 for r in rows if r.get("status") == "xpassed")
        # An XPASS did pass — excluding it would make a run that just fixed a
        # documented bug look like it regressed.
        rate    = f"{((passed + xpassed) / total * 100):.0f}%" if total else "—"
        row_bg  = _DARK_BG if row_idx % 2 == 0 else _HEADER_BG

        # A feature can span several make targets (e.g. test_17's two
        # classes); show the whole-file one when there is a single clean
        # `pytest tests/<file>.py` recipe for it, else leave it blank rather
        # than guess which of several per-class/per-test targets to name.
        group_targets = {r.get("make_group") for r in rows if r.get("make_group")}
        command = f"make {next(iter(group_targets))}" if len(group_targets) == 1 else ""

        values = [command, group, total, passed, failed, skipped, xfailed, xpassed, rate, f"{_duration_seconds(rows):.0f}s"]
        for col_idx, value in enumerate(values, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.border    = _thin_border()
            cell.fill      = _fill(row_bg)
            cell.font      = _font(color=_FAIL_FG if failed else (_XPASS_FG if xpassed else _WHITE))
            cell.alignment = _center() if col_idx > 2 else _left()

    ws.auto_filter.ref = ws.dimensions


# ── Public entry point ────────────────────────────────────────────────────────

def generate_excel_report(
    results: list,
    output_path: str = "test-report.xlsx",
) -> str:
    """Generate a formatted Excel workbook: per-test Results (grouped by
    feature, failures floated up) plus a By Command summary sheet.

    Args:
        results:     List of dicts with keys node_id, name, status, duration, error.
        output_path: Destination file path for the .xlsx file.

    Returns:
        The resolved output path string.
    """
    wb = Workbook()
    wb.active.title = "Results"
    ws_results = wb.active
    _write_results(ws_results, _ordered_results(results))

    ws_by_command = wb.create_sheet("By Command")
    _write_by_command(ws_by_command, results)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    return str(Path(output_path).resolve())
