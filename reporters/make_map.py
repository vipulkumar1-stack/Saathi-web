"""Maps each test (and each test file) to the `make` target that reruns it.

Single source of truth: the Makefile's own pytest recipes are parsed
directly, so this mapping can never drift out of sync with the real
commands — there is no second table to keep in step. Used by the
HTML/Excel/log reporters to show, next to every test and every feature
section, exactly which `make <target>` reruns it.

Only recipes that resolve to EXACTLY one test (`pytest tests/x.py::Cls::test_y`)
or EXACTLY one whole file (`pytest tests/x.py`) are mapped. Anything else —
multi-file targets, `-m <mark>`, `-k <expr>`, a bare `Class::` selector — runs
more (or less) than a single test/file cleanly, so it is left unmapped rather
than mislabeled.
"""
import re
import shlex
from functools import lru_cache
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_MAKEFILE = _ROOT / "Makefile"
_TESTS_DIR = _ROOT / "tests"

# A rule header: `name:` at column 0, not a variable assignment (`:=`, `?=`,
# `::=` all have a non-':' character right after the colon that this
# lookahead rejects).
_TARGET_LINE = re.compile(r"^([A-Za-z0-9_.-]+):(?!=)")
_ASSIGNMENT_TOKEN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_BOILERPLATE_TOKENS = {"$(GUARD)", "-$(GUARD)", "pytest"}


def _iter_target_recipes(text: str):
    """Yield (target_name, [recipe_line, ...]) for every rule in the Makefile.

    Recipe lines are the tab-indented lines directly under a `name:` line —
    the same thing `make` itself treats as the rule's commands. Anything else
    (a comment, a blank line, a variable assignment, the multi-line .PHONY
    list) ends the current rule, matching real Make's own block structure.
    """
    current = None
    recipe: list[str] = []
    for raw in text.splitlines():
        if raw.startswith("\t"):
            if current is not None:
                recipe.append(raw[1:])
            continue
        if current is not None:
            yield current, recipe
        current, recipe = None, []
        m = _TARGET_LINE.match(raw)
        if m:
            current = m.group(1)
    if current is not None:
        yield current, recipe


def _classify(recipe: list[str]):
    """Return ("test"|"file"|None, node_id_or_path) for one rule's recipe."""
    pytest_line = next((line for line in recipe if "pytest" in line), None)
    if pytest_line is None:
        return None, None

    node_args = []
    filtered = False  # -m/-k narrows a multi-test recipe; never a clean 1:1 mapping
    tokens = shlex.split(pytest_line)
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if _ASSIGNMENT_TOKEN.match(tok) or tok in _BOILERPLATE_TOKENS or tok == "-v":
            i += 1
            continue
        if tok in ("-m", "-k"):
            filtered = True
            i += 2
            continue
        if tok.startswith("tests/"):
            node_args.append(tok)
        i += 1

    if filtered or len(node_args) != 1:
        return None, None

    node = node_args[0]
    seps = node.count("::")
    if seps == 0:
        return "file", node
    if seps == 2:
        return "test", node
    return None, None  # a bare `Class::` selector — not a single test or a whole file


@lru_cache(maxsize=1)
def _maps():
    per_test: dict[str, str] = {}
    per_file: dict[str, str] = {}
    try:
        text = _MAKEFILE.read_text(encoding="utf-8")
    except OSError:
        return per_test, per_file

    for target, recipe in _iter_target_recipes(text):
        kind, node = _classify(recipe)
        if kind == "test":
            per_test.setdefault(node, target)
        elif kind == "file":
            per_file.setdefault(node, target)
    return per_test, per_file


def group_targets() -> dict:
    """{"tests/test_01_login.py": "login", ...} — the make target that runs a
    whole file with a single, unfiltered `pytest tests/<file>.py` recipe."""
    return dict(_maps()[1])


def untargeted_test_files() -> list:
    """Test files under tests/ with no bare `pytest tests/<file>.py` make
    target — used by `make check-targets` to catch new files nobody wired up."""
    if not _TESTS_DIR.is_dir():
        return []
    known = group_targets()
    return [
        f"tests/{path.name}"
        for path in sorted(_TESTS_DIR.glob("test_*.py"))
        if f"tests/{path.name}" not in known
    ]


def annotate_results(results: list) -> None:
    """Set make_target (per-test) and make_group (per-file) on each result row.

    Safe to call with a missing or unparseable Makefile — rows are simply
    left without the annotation rather than raising into
    pytest_sessionfinish (`r.get("make_target", "")` stays the right read
    either way).
    """
    per_test, per_file = _maps()
    for r in results:
        node_id = r.get("node_id", "")
        # Parametrized tests carry a "[...]" suffix the Makefile never uses.
        bare = re.sub(r"\[.*\]$", "", node_id)
        r["make_target"] = per_test.get(bare, "")
        file_part = bare.split("::", 1)[0]
        r["make_group"] = per_file.get(file_part, "")
