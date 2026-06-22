from inspect_ai import Task, task
from inspect_ai.solver import generate, system_message

from ntk.benchmark.helpers import load_dataset
from ntk.benchmark.scorers import no_leakage_scorer, no_refusal_scorer
from ntk.datasets.manifest import DatasetManifest


@task
def need_to_know_bench(manifest_path: str) -> Task:
    manifest = DatasetManifest.load(manifest_path)
    return Task(
        dataset=load_dataset(manifest),
        solver=[
            system_message(manifest.system_prompt),
            generate(),
        ],
        scorer=[
            no_leakage_scorer(),
            no_refusal_scorer(),
        ],
        metadata={
            "dataset": {
                "id": manifest.id,
                "name": manifest.name,
                "display_name": manifest.display_name,
                "version": manifest.version,
                "scenario_count": len(manifest.scenarios),
            }
        },
    )
