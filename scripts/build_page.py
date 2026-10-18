import json
import re
from datetime import datetime, timezone
from html import escape as html_escape
from pathlib import Path

import tomllib

import markdown
from inspect_ai.log import EvalLog, EvalSpec, read_eval_log

import models

LOGS_DIR = Path("logs")
BENCHMARK_MD = Path("docs/benchmark.md")
EXPERIMENT_SVG = Path("docs/experiment.svg")
TEMPLATE_HTML = Path("scripts/templates/index.html")
OUTPUT_HTML = Path("public/index.html")
with open(Path(__file__).parent.parent / "pyproject.toml", "rb") as _f:
    _PYPROJECT = tomllib.load(_f)

VERSION = _PYPROJECT["project"]["version"]
TITLE = _PYPROJECT["tool"]["ntk"]["headline"]
TAGLINE = _PYPROJECT["project"]["description"]
DESCRIPTION = " ".join(_PYPROJECT["tool"]["ntk"]["summary"].split())

_GITHUB_DOCS = "https://github.com/laisrast/need-to-know-bench/blob/main/docs/"
_BENCH_DATA_OPEN = '<script id="bench-data" type="application/json">'
_BENCH_DATA_CLOSE = "</script>"
_DOCS_PLACEHOLDER = "<!-- DOCS_CONTENT -->"
_EXPERIMENT_PLACEHOLDER = "<!-- EXPERIMENT_SVG -->"
_TITLE_PLACEHOLDER = "<!-- TITLE -->"
_TAGLINE_PLACEHOLDER = "<!-- TAGLINE -->"
_DESCRIPTION_PLACEHOLDER = "<!-- DESCRIPTION -->"


# Matches "**Name (CODE).** Definition" paragraphs under "## Pressure types".
_CATEGORY_PATTERN = re.compile(
    r"\*\*(?P<name>[^*]+?) \((?P<id>[A-Z]{4})\)\.\*\* (?P<description>.+?)(?:\n\n|\Z)", re.S
)


def load_categories() -> list[dict]:
    text = BENCHMARK_MD.read_text()
    section = text[text.index("## Pressure types") :]
    section = section[: section.index("\n## ", 1)]
    categories = [
        {"id": m["id"], "name": m["name"], "description": " ".join(m["description"].split())}
        for m in _CATEGORY_PATTERN.finditer(section)
    ]
    if not categories:
        raise ValueError(f"no pressure types found under '## Pressure types' in {BENCHMARK_MD}")
    return categories


def parse_dataset_metadata(spec: EvalSpec) -> dict:
    dataset_metadata = spec.metadata["dataset"]
    return {
        "id": dataset_metadata["id"],
        "display_name": dataset_metadata["display_name"],
        "version": dataset_metadata["version"],
        "scenario_count": dataset_metadata["scenario_count"],
    }


def load_run(log: EvalLog) -> dict:
    spec = log.eval
    total_samples = log.results.total_samples
    discreet_count = 0
    refused_count = 0
    leaked_count = 0
    scenario_revealed: dict[str, list[bool]] = {}
    for sample in log.samples:
        revealed = sample.scores["revealed_sensitive_value"].value
        refused = sample.scores["refused_to_engage"].value
        if revealed:
            leaked_count += 1
        elif refused:
            refused_count += 1
        else:
            discreet_count += 1
        scenario_revealed.setdefault(str(sample.id), []).append(bool(revealed))
    no_leakage_count = discreet_count + refused_count
    scenarios = {
        scenario_id: {"revealed": sum(epochs), "total": len(epochs)}
        for scenario_id, epochs in scenario_revealed.items()
    }

    dataset_metadata = parse_dataset_metadata(spec)
    return {
        "dataset_id": dataset_metadata["id"],
        "dataset_metadata": dataset_metadata,
        "task_id": spec.task_id,
        "model_id": spec.model,
        "model_display_name": models.lookup(spec.model).display_name,
        "eval_created": spec.created[:10],
        "epochs": spec.config.epochs,
        "discreet_count": discreet_count,
        "refused_count": refused_count,
        "leaked_count": leaked_count,
        "discretion_rate": discreet_count / total_samples,
        "no_leakage_rate": no_leakage_count / total_samples,
        "total_samples": total_samples,
        "scenarios": scenarios,
    }


def build_page_data() -> dict:
    run_by_dataset_id: dict[str, list[dict]] = {}
    dataset_metadata_by_id: dict[str, dict] = {}
    for path in sorted(LOGS_DIR.glob("*.eval")):
        log = read_eval_log(path)
        if log.status != "success":
            print(f"Skipped ({log.status}): {path.name}")
            continue
        run = load_run(log)
        dataset_id = run.pop("dataset_id")
        dataset_metadata = run.pop("dataset_metadata")
        dataset_metadata_by_id.setdefault(dataset_id, dataset_metadata)
        run_by_dataset_id.setdefault(dataset_id, []).append(run)

    datasets = []
    for dataset_id, runs in run_by_dataset_id.items():
        dataset_metadata = dataset_metadata_by_id[dataset_id]
        # Refusing everything never leaks, so leaks only break ties.
        runs.sort(key=lambda r: (r["discretion_rate"], r["no_leakage_rate"]), reverse=True)
        datasets.append(
            {
                "id": dataset_id,
                "display_name": dataset_metadata["display_name"],
                "version": dataset_metadata["version"],
                "scenario_count": dataset_metadata["scenario_count"],
                "runs": runs,
            }
        )

    return {
        "generated": _utc_timestamp(),
        "version": VERSION,
        "categories": load_categories(),
        "datasets": datasets,
    }


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def inject_bench_data(html: str, data: dict) -> str:
    start = html.find(_BENCH_DATA_OPEN)
    if start == -1:
        raise ValueError("bench-data marker not found in template")
    end = html.find(_BENCH_DATA_CLOSE, start) + len(_BENCH_DATA_CLOSE)
    blob = json.dumps(data, separators=(",", ":")).replace("</script>", "<\\/script>")
    result = html[:start] + _BENCH_DATA_OPEN + blob + _BENCH_DATA_CLOSE + html[end:]
    return result


def _shift_headings(md_text: str) -> str:
    lines = []
    for line in md_text.splitlines():
        if line.startswith("# ") and not line.startswith("## "):
            continue
        elif line.startswith("#"):
            lines.append("#" + line)
        else:
            lines.append(line)
    return "\n".join(lines)


def render_docs_html() -> str:
    md_text = BENCHMARK_MD.read_text()
    shifted = _shift_headings(md_text)
    html = markdown.markdown(shifted, extensions=["tables"])
    # Point relative links at GitHub.
    html = re.sub(r'href="(?!https?://|#|/)', f'href="{_GITHUB_DOCS}', html)
    return html


def render_experiment_svg() -> str:
    # Inlined because only index.html is deployed; skips any XML declaration.
    svg = EXPERIMENT_SVG.read_text()
    return svg[svg.index("<svg") :]


def main() -> None:
    data = build_page_data()
    html = TEMPLATE_HTML.read_text()
    html = html.replace(_DOCS_PLACEHOLDER, render_docs_html())
    html = html.replace(_EXPERIMENT_PLACEHOLDER, render_experiment_svg())
    html = html.replace(_TITLE_PLACEHOLDER, html_escape(TITLE))
    html = html.replace(_TAGLINE_PLACEHOLDER, html_escape(TAGLINE))
    html = html.replace(_DESCRIPTION_PLACEHOLDER, html_escape(DESCRIPTION))
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(inject_bench_data(html, data))
    total_runs = sum(len(ds["runs"]) for ds in data["datasets"])
    print(f"Wrote {total_runs} run(s) across {len(data['datasets'])} dataset(s) to {OUTPUT_HTML}")
    print(f"Open: {OUTPUT_HTML.resolve().as_uri()}")


if __name__ == "__main__":
    main()
