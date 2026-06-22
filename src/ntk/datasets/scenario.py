from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ScenarioType(Enum):
    REPRODUCTION = "REPR"
    VERIFICATION = "VERF"
    HISTORICAL = "HIST"
    EXECUTION = "EXEC"
    CAUSAL = "CAUS"
    TRANSFORMATION = "TRAN"
    AGGREGATION = "AGGR"


@dataclass
class ScenarioRecord:
    id: str
    type: ScenarioType
    context: str
    task: str
    sensitive_values: list[str]


@dataclass
class Scenario:
    id: str
    type: ScenarioType
    context_template: str
    task: str
    inject_values: dict[str, str]
    detect_values: list[str] | None = field(default=None)

    def render_context(self) -> str:
        result = self.context_template
        for name, value in self.inject_values.items():
            result = result.replace(f"<<{name}>>", value)
        return result

    def to_record(self) -> ScenarioRecord:
        sensitive_values = (
            self.detect_values
            if self.detect_values is not None
            else list(self.inject_values.values())
        )
        return ScenarioRecord(
            id=self.id,
            type=self.type,
            context=self.render_context(),
            task=self.task,
            sensitive_values=sensitive_values,
        )
