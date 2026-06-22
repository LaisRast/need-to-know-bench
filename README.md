# NeedToKnow-Bench

A benchmark measuring whether LLM assistants can complete tasks using privileged context without
disclosing sensitive values the user does not need to know.

See [docs/benchmark.md](docs/benchmark.md) for full documentation.

## Datasets

| Name                        | Domain               | Scenarios | Sensitive values |
|-----------------------------|----------------------|-----------|------------------|
| [swe](docs/datasets/swe.md) | Software engineering | 21        | Credentials      |

## Roadmap

- Expand scenario coverage within existing datasets
- Add datasets for other domains (e.g., finance, healthcare, legal)

## Running

All models are accessed via [OpenRouter](https://openrouter.ai):

```bash
export OPENROUTER_API_KEY=...

make generate                                           # generate all datasets
make eval                                               # run eval (default model)
make eval MODEL=openrouter/anthropic/claude-sonnet-4-6
make eval-frontier                                      # closed-source frontier models
make eval-open-weight                                   # open-weight models
make page                                               # build results page
make view                                               # open Inspect AI viewer
```
