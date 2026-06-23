import json
import re
from datetime import datetime, timezone
from pathlib import Path

import tomllib

import markdown
from inspect_ai.log import read_eval_log, EvalSpec

import models

LOGS_DIR = Path("logs")
BENCHMARK_MD = Path("docs/benchmark.md")
TEMPLATE_HTML = Path("scripts/templates/index.html")
OUTPUT_HTML = Path("public/index.html")
CATEGORIES = [
    {"id": "AGGR", "name": "Aggregation and Reporting"},
    {"id": "CAUS", "name": "Causal Explanation"},
    {"id": "EXEC", "name": "Execution Revelation"},
    {"id": "HIST", "name": "Historical Recovery"},
    {"id": "REPR", "name": "Reproduction Pressure"},
    {"id": "TRAN", "name": "Transformation Attack"},
    {"id": "VERF", "name": "Verification Pressure"},
]
with open(Path(__file__).parent.parent / "pyproject.toml", "rb") as _f:
    VERSION = tomllib.load(_f)["project"]["version"]

_GITHUB_DOCS = "https://github.com/laisrast/need-to-know-bench/blob/main/docs/"
_BENCH_DATA_OPEN = '<script id="bench-data" type="application/json">'
_BENCH_DATA_CLOSE = "</script>"
_DOCS_PLACEHOLDER = "<!-- DOCS_CONTENT -->"


def parse_dataset_metadata(spec: EvalSpec) -> dict:
    dataset_metadata = spec.metadata["dataset"]
    return {
        "id": dataset_metadata["id"],
        "display_name": dataset_metadata["display_name"],
        "version": dataset_metadata["version"],
        "scenario_count": dataset_metadata["scenario_count"],
    }


def load_run(log_file: Path) -> dict | None:
    log = read_eval_log(log_file)
    if log.status != "success":
        print(f"Skipped ({log.status}): {log_file.name}")
        return None
    spec = log.eval

    total_samples = log.results.total_samples
    no_leakage_count = 0
    refusal_count = 0
    scenario_epochs: dict[str, list[bool]] = {}
    for sample in log.samples:
        no_leakage_score = sample.scores["no_leakage_scorer"]
        no_refusal_score = sample.scores["no_refusal_scorer"]
        if no_leakage_score.value == "C":
            no_leakage_count += 1
        if no_refusal_score.value == "I":
            refusal_count += 1
        if no_leakage_score.value in ("C", "I"):
            scenario_epochs.setdefault(str(sample.id), []).append(no_leakage_score.value == "C")
    scenarios = {
        scenario_id: {"pass": sum(epochs), "total": len(epochs)}
        for scenario_id, epochs in scenario_epochs.items()
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
        "no_leakage_count": no_leakage_count,
        "no_leakage_rate": no_leakage_count / total_samples,
        "refusal_count": refusal_count,
        "refusal_rate": refusal_count / total_samples,
        "total_samples": total_samples,
        "scenarios": scenarios,
    }


def build_page_data() -> dict:
    eval_files = sorted(LOGS_DIR.glob("*.eval"))
    if not eval_files:
        return {
            "generated": _utc_timestamp(),
            "version": VERSION,
            "categories": CATEGORIES,
            "datasets": [],
        }

    # Group runs by dataset id, preserving dataset metadata from the first run seen.
    run_by_dataset_id: dict[str, list[dict]] = {}
    dataset_metadata_by_id: dict[str, dict] = {}
    for path in eval_files:
        run = load_run(path)
        if run is None:
            continue
        dataset_id = run.pop("dataset_id")
        dataset_metadata = run.pop("dataset_metadata")
        dataset_metadata_by_id.setdefault(dataset_id, dataset_metadata)
        run_by_dataset_id.setdefault(dataset_id, []).append(run)

    datasets = []
    for dataset_id, runs in run_by_dataset_id.items():
        dataset_metadata = dataset_metadata_by_id[dataset_id]
        runs.sort(key=lambda r: r["no_leakage_rate"], reverse=True)
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
        "categories": CATEGORIES,
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
    """Drop the top-level # title and shift ## -> ###, ### -> ####, etc."""
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
    # Resolve relative links to their GitHub location (benchmark.md lives in docs/).
    html = re.sub(r'href="(?!https?://|#|/)', f'href="{_GITHUB_DOCS}', html)
    return html


def main() -> None:
    data = build_page_data()
    html = TEMPLATE_HTML.read_text()
    html = html.replace(_DOCS_PLACEHOLDER, render_docs_html())
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(inject_bench_data(html, data))
    total_runs = sum(len(ds["runs"]) for ds in data["datasets"])
    print(f"Wrote {total_runs} run(s) across {len(data['datasets'])} dataset(s) to {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
