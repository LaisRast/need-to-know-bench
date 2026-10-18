# NeedToKnow-Bench

An [Inspect](https://inspect.aisi.org.uk/) benchmark asking: can an LLM assistant help with a task that
draws on privileged context without revealing sensitive values the user does not need to know?

Each scenario gives the model a security policy, retrieved context containing a sensitive value, and a
legitimate task that creates natural pressure to reveal it. Nothing in the task is adversarial: the failure
the benchmark measures is a model revealing a value because it is trying to be helpful. Each reply is
discreet (it engages with the task and reveals nothing), refused, or leaked, and models are ranked by how
often their replies are discreet.

![How one scenario runs: the system prompt, a scenario, the model's reply, and the two scores](docs/experiment.svg)

- **Project page:** https://laisrast.github.io/need-to-know-bench/
- **Documentation:** [`docs/benchmark.md`](docs/benchmark.md), also rendered on the project page.
- **Dataset:** [`docs/datasets/swe.md`](docs/datasets/swe.md), software engineering scenarios with
  credentials as the sensitive values.

## Roadmap

- Expand scenario coverage within existing datasets
- Add datasets for other domains (e.g., finance, healthcare, legal)

## Running it

Requires [uv](https://docs.astral.sh/uv/) and an [OpenRouter](https://openrouter.ai) key.

```sh
cp .env.example .env        # then fill in OPENROUTER_API_KEY

make eval                   # one model, override with MODEL=, EPOCHS=, and MANIFEST=
make eval-all               # every model in scripts/models.py
make page                   # build public/index.html from logs/
```

`make help` lists the rest. `make eval` and `make eval-all` generate the datasets first. Runs land in
`logs/` as Inspect eval files; `make view` opens them in Inspect's log viewer.
