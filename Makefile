MODEL    ?= openrouter/openai/gpt-4o-mini
EPOCHS   ?= 1
MANIFEST ?= data/swe_0.1.0-preview.json

# Resolve MANIFEST relative to the inspect task file directory (where inspect_ai chdirs to).
_MANIFEST = $(shell realpath --relative-to=src/ntk/benchmark $(abspath $(MANIFEST)))

.PHONY: generate eval eval-all page view report fmt clean help

help:
	@echo "make generate                            Generate all datasets"
	@echo "make eval                                Run eval (default model: $(MODEL), manifest: $(MANIFEST))"
	@echo "make eval MODEL=  EPOCHS=  MANIFEST=     Run eval with specific options"
	@echo "make eval-all                            Run full model suite"
	@echo "make page                                Build public/index.html from logs/"
	@echo "make view                                Open Inspect AI results viewer"
	@echo "make report                              Build overview.svg and heatmap.svg"
	@echo "make fmt                                 Format code with ruff"
	@echo "make clean                               Remove generated artifacts"

generate:
	uv run python -m ntk.datasets.generate
	mkdir -p data
	mv src/ntk/datasets/generated/* data/
	rm -r src/ntk/datasets/generated/

eval: generate
	uv run inspect eval src/ntk/benchmark/task.py -T manifest_path=$(_MANIFEST) --model $(MODEL) --epochs $(EPOCHS)

eval-all: generate
	uv run python scripts/run_evals.py --epochs $(EPOCHS) --manifest-path $(_MANIFEST)

page:
	uv run python scripts/build_page.py

view:
	uv run inspect view

fmt:
	uv run ruff format src/ scripts/

clean:
	rm -rf public/
	rm -rf data/
	rm -rf logs/
	rm -rf src/ntk/datasets/generated/
