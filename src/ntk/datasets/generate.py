from pathlib import Path

from ntk.datasets.manifest import Dataset
from ntk.datasets.swe.dataset import dataset as _swe

_DATASETS: list[Dataset] = [
    _swe,
]

_OUT_DIR = Path(__file__).parent / "generated"


def _generate_one(dataset: Dataset) -> None:
    manifest = dataset.to_manifest()
    path = _OUT_DIR / f"{manifest.id}.json"
    manifest.save(path)
    print(f"Built {len(manifest.scenarios)} {manifest.name} scenarios -> {path}")


def generate() -> None:
    _OUT_DIR.mkdir(exist_ok=True)
    for dataset in _DATASETS:
        _generate_one(dataset)


if __name__ == "__main__":
    generate()
