from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from ntk.datasets.scenario import Scenario, ScenarioRecord, ScenarioType


@dataclass
class Dataset:
    name: str
    display_name: str
    version: str
    system_prompt: str
    scenarios: list[Scenario]

    @property
    def id(self) -> str:
        return f"{self.name}_{self.version}"

    def to_manifest(self) -> DatasetManifest:
        return DatasetManifest(
            id=self.id,
            name=self.name,
            display_name=self.display_name,
            version=self.version,
            system_prompt=self.system_prompt,
            scenarios=[s.to_record() for s in self.scenarios],
        )


@dataclass
class DatasetManifest:
    id: str
    name: str
    display_name: str
    version: str
    system_prompt: str
    scenarios: list[ScenarioRecord]

    def save(self, path: str | Path) -> None:
        data = dataclasses.asdict(self)
        with Path(path).open("w") as f:
            json.dump(data, f, indent=2, default=lambda o: o.value if isinstance(o, Enum) else o)

    @classmethod
    def load(cls, path: str | Path) -> DatasetManifest:
        with Path(path).open() as f:
            data = json.load(f)
        return cls(
            id=data.get("id", f"{data['name']}_{data['version']}"),
            name=data["name"],
            display_name=data.get("display_name", data["name"]),
            version=data["version"],
            system_prompt=data["system_prompt"],
            scenarios=[
                ScenarioRecord(
                    id=s["id"],
                    type=ScenarioType(s["type"]),
                    context=s["context"],
                    task=s["task"],
                    sensitive_values=s["sensitive_values"],
                )
                for s in data["scenarios"]
            ],
        )
