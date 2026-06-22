import argparse
import subprocess
import sys

from models import REGISTRY, Model


def run_models(models: list[Model], manifest_path: str, epochs: int) -> None:
    for model in models:
        print(f"=== {model.display_name} ===")
        result = subprocess.run(
            [
                "uv",
                "run",
                "inspect",
                "eval",
                "src/ntk/benchmark/task.py",
                "-T",
                f"manifest_path={manifest_path}",
                "--model",
                model.id,
                "--epochs",
                str(epochs),
            ]
        )
        if result.returncode != 0:
            print(f"FAILED: {model.id}", file=sys.stderr)
            sys.exit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run NeedToKnow-Bench evaluations")
    parser.add_argument("--epochs", type=int, required=True)
    parser.add_argument("--manifest-path", required=True)
    args = parser.parse_args()
    run_models(REGISTRY, args.manifest_path, args.epochs)


if __name__ == "__main__":
    main()
