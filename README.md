# Quanta-Ask

Quanta-Ask studies whether tool-using LLM agents confuse task relevance with user authorization, and whether risk-aware clarification, temporal authorization monitoring, and minimal repair can close that gap without destroying task utility.

## Phase 0–1 scope

- Main line: missing/ambiguous authorization before consequential tool calls.
- Secondary line A: authorization forgetting in long trajectories.
- Secondary line B: provenance-aware handling of indirect prompt injection, evaluated later with AgentDojo.

The first milestone is **problem validation**, not a claimed defense result. The repository therefore starts with a controlled paired benchmark, deterministic metrics, replay baselines, and an OpenAI-compatible model adapter suitable for a local vLLM server.

## Repository layout

```text
docs/                         research design, technical specification, experiment report
data/seeds/                   human-reviewable benchmark seeds
src/quanta_ask/               benchmark schema, generation, policies and evaluation
scripts/                      reproducible command-line entry points
tests/                        offline unit and regression tests
server/                       scripts constrained to the dedicated server project directory
```

## Quick start

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"
.venv/Scripts/python -m pytest
.venv/Scripts/python scripts/build_phase1_dataset.py
.venv/Scripts/python scripts/run_baseline.py --policy heuristic
```

For an OpenAI-compatible endpoint:

```bash
python scripts/run_baseline.py \
  --policy openai-compatible \
  --base-url http://127.0.0.1:8000/v1 \
  --model <served-model-id>
```

No real external action is executed. Every tool call is evaluated in a typed simulator.

## Research records

- [Research design](docs/research_design.md)
- [Technical specification](docs/technical_spec.md)
- [Experiment report](docs/experiment_report.md)

