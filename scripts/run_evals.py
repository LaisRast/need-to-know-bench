import argparse
import subprocess
import sys

from models import REGISTRY


def main() -> None:
    parser = argparse.ArgumentParser(description="Run NeedToKnow-Bench across the model registry")
    parser.add_argument("--epochs", type=int, required=True)
    parser.add_argument("--manifest-path", required=True)
    args = parser.parse_args()

    models = ",".join(model.id for model in REGISTRY)
    result = subprocess.run(
        [
            "uv",
            "run",
            "inspect",
            "eval",
            "src/ntk/benchmark/task.py",
            "-T",
            f"manifest_path={args.manifest_path}",
            "--model",
            models,
            "--epochs",
            str(args.epochs),
            "--timeout",
            "60",
            "--max-retries",
            "3",
        ]
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
