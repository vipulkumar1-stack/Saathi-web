"""Generate a self-contained, single-file Allure HTML report.

`pytest --alluredir=allure-results` only writes raw result JSON; a viewable
report is produced by the Allure CLI. `allure generate --single-file` bundles
the whole report into one standalone `index.html` that opens in any browser
offline — ideal for emailing as an attachment (no server, no asset folder).

The Allure CLI is located from (in order): the ALLURE_BIN env var, the
project's conventional install path (~/allure/bin/allure — the same one the
Makefile uses), then whatever is on PATH. If none is found, or there are no
results, generation is skipped so a run never fails over reporting.
"""
import os
import shutil
import subprocess
from pathlib import Path


def _find_allure() -> str | None:
    candidates = [
        os.getenv("ALLURE_BIN", "").strip(),
        str(Path.home() / "allure" / "bin" / "allure"),
    ]
    for c in candidates:
        if c and Path(c).is_file():
            return c
    return shutil.which("allure")


def _java_env() -> dict:
    """Return an env where JAVA_HOME is valid.

    The Allure launcher hard-fails if JAVA_HOME is set to a non-existent
    directory (as it is in this environment) even when a working `java` is on
    PATH. So when JAVA_HOME is missing or invalid, derive it from PATH's java,
    or drop it entirely so the launcher falls back to `java`.
    """
    env = dict(os.environ)
    jh = env.get("JAVA_HOME", "")
    if jh and (Path(jh) / "bin" / "java").is_file():
        return env
    java = shutil.which("java")
    if java:
        env["JAVA_HOME"] = str(Path(java).resolve().parent.parent)
    else:
        env.pop("JAVA_HOME", None)
    return env


def generate_single_file_report(
    results_dir: str = "allure-results",
    output_file: str = "allure-report.html",
) -> str | None:
    """Generate a single-file Allure report and return its path.

    Returns None when there are no results to render. Raises RuntimeError /
    CalledProcessError on a missing CLI or a failed generation so the caller
    can log it (the caller wraps this in try/except).
    """
    results = Path(results_dir)
    if not results.is_dir() or not any(results.iterdir()):
        return None

    allure = _find_allure()
    if not allure:
        raise RuntimeError(
            "Allure CLI not found — set ALLURE_BIN, install to ~/allure/bin/allure, "
            "or add 'allure' to PATH."
        )

    out_dir = Path("allure-report")
    subprocess.run(
        [allure, "generate", str(results), "-o", str(out_dir), "--clean", "--single-file"],
        check=True,
        capture_output=True,
        text=True,
        timeout=180,
        env=_java_env(),
    )

    single = out_dir / "index.html"
    if not single.is_file():
        return None

    # Copy to a descriptive filename so the email attachment isn't "index.html".
    dest = Path(output_file)
    shutil.copyfile(single, dest)
    return str(dest)
