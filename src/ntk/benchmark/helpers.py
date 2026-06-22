import json

from inspect_ai.dataset import MemoryDataset, Sample

from ntk.datasets.manifest import DatasetManifest


def parse_json_response(completion: str) -> dict:
    original = completion
    completion = completion.strip()
    if completion.startswith("```"):
        completion = completion.split("\n", 1)[1].rsplit("```", 1)[0]
    try:
        return json.loads(completion.strip())
    except (json.JSONDecodeError, AttributeError) as e:
        raise RuntimeError(f"Failed to parse JSON from model response: {original!r}") from e


def load_dataset(manifest: DatasetManifest) -> MemoryDataset:
    samples = [
        Sample(
            id=s.id,
            input=f"{s.task}\n\n[Context]\n\n{s.context}",
            metadata={
                "sensitive_values": s.sensitive_values,
                "scenario_type": s.type.value,
                "task": s.task,
            },
        )
        for s in manifest.scenarios
    ]
    return MemoryDataset(samples, name=manifest.name)
