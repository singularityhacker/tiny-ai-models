# Tiny Models, Part II — bounded pilot

**Latest proposal:** [Bedrock blueprint v0.2](blueprint/README.md) proposes
Ministral 3 3B, managed Knowledge Bases and Bedrock Evaluations. Part II uses a
new generated-answer protocol, with no direct comparison claim against Part I.
The user approved this direction and proceeding to preflight with the proposed
one-model study. [Preflight findings](bedrock/README.md) record the current
smoke results and AWS account-verification hold. Execution readiness is separate
from plan approval.

**Legacy scaffolding below:** the local likelihood runner and `configs/pilot.json`
do not implement the Bedrock proposal. The config remains disabled. The older
scope and next steps below are historical implementation notes, superseded by
the v0.2 blueprint; do not use them as execution authorization.

The experiment tools remain independent of the published 2025 dashboard.
The authorized blueprint publication adds a link and a separate `/part-ii/`
page through the existing build script; historical results stay unchanged.
The experiment commands below create no cloud resources or public release.

## Previous pilot scope (superseded)

- MMLU and HellaSwag, using lm-eval likelihood scoring. Keep HellaSwag raw
  accuracy and length-normalized accuracy separate.
- Original **Llama 3.2 3B base** checkpoint plus two current small candidates,
  selected after checking weights, licenses, compatibility and hosting prices.
  The current-model slots are deliberately unfilled, not invented model IDs.
- No retrieval, single search, multiple searches with deduplication and reranking.
- Two questions per MMLU subject (114) plus 100 HellaSwag questions = **214
  shared questions; 1,926 scored answers across three models and three arms**.
  Four candidate continuations per item mean 7,704 likelihood evaluations,
  not 1,926 generation API calls. This is an exploratory panel.
- $200 total ceiling, $100 target, first cloud pilot at most $20, at least 20%
  contingency. Infrastructure idle time, storage/network, retries and retrieval
  count toward the ceiling. Unknown costs block readiness in the planner.

## Working now (no cloud or ML dependencies)

From this directory:

```sh
python -m tinybench plan
python -m tinybench audit-history --out artifacts/history.json
python -m tinybench report
python -m unittest discover -s tests -v
```

The history importer preserves source checksums and marks recovered scores as
historical aggregates, not item-level verified results. Output files are
exclusive-create to avoid accidentally replacing an evidence artifact.

The report writes `preview/index.html`, rejects writes to production `dist/`,
and shows an explicit empty state until completed runs exist. It escapes labels,
checks result checksums, and does not embed question-level raw data in the page.
It is an experimental preview, not a publish validator or verified leaderboard.

## Optional local benchmark adapter

The commands below describe the post-approval workflow. `prepare` and `run`
currently refuse execution because `execution_approved` is false. Set it only
after Justice approves the final protocol, architecture and cost plan; then
freeze a new panel under that approved configuration.

Use a separate Python environment; do not upgrade the original `../venv`:

```sh
uv venv --python 3.11
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m tinybench prepare --out artifacts/panel.json
.venv/bin/python -m tinybench run --panel artifacts/panel.json \
  --model historical-3b --arm none --device mps --out artifacts/runs/anchor-none
python -m tinybench report
```

`prepare` downloads benchmark data through the harness. `run` downloads/loads
model weights and uses the selected device; gated weights require the user's
existing Hugging Face access. Neither command provisions infrastructure.
The adapter is implemented but has not yet completed a real inference run.
Only the harness is pinned currently; a full dependency/container lock is still
required before cloud execution. Do not interpret local-run timing as AWS timing.

The panel freezes task-local IDs, hashes of the selected records, harness
version and configuration hash. The runner refuses changed records/configs,
uses zero-shot scoring, logs per-item harness outputs, rejects oversized
prompts and writes a completion checksum only after a successful run. Failed
runs stay on disk. There is no automatic retry or item-level resume yet.

## Retrieval contract

`tinybench.retrieval.retrieve` accepts a search provider, reranker and tokenizer.
It performs four actual searches in `multi_rerank`: the question and three
distinct frozen variants. It deduplicates text, combines ranks using reciprocal
rank fusion, reranks against the original question, and packs complete chunks
within a shared token budget. It records candidates, rankings and exclusions.
Queries come from the question stem/context, never choices or gold labels.

Provider wiring and rewrite generation remain to be implemented after the
AWS route is chosen. No lexical stub is presented as neural reranking.
The runner's `--evidence` input accepts a precomputed JSON envelope:

```json
{"panel_sha256":"<digest of panel JSON>","arm":"multi_rerank",
 "items":{"mmlu_global_facts:42":{"context":"[chunk-id] Evidence text"}}}
```

Every panel item must be present. Generate the evidence once per arm and reuse
it for every model. A separate uncached experiment will be needed for retrieval
latency. Evidence files are trusted local inputs at this stage; validate their
token budgets, corpus provenance and traces before using real study results.

## Historical finding

The full 2025 baseline file records `meta-llama/Llama-3.2-3B` (base), model SHA
`13afe5124825b4f3751f836b40dafda64c1ed062`, BF16 on MPS:

- MMLU accuracy: 53.9168%, 14,042 questions.
- HellaSwag accuracy: 55.2480%; normalized accuracy: 73.5312%, 10,042 questions.

The recovered file does not establish a 1B run. These are preserved historical
aggregates; replay requires original item-level evidence. Part II subsets,
zero-shot settings and new harness/data versions must not be described as an
exact reproduction of the original full run.

## Previous implementation gates (superseded)

1. Resolve the AWS account/profile and region. Select and pin the two new models.
2. Lock dependencies, prepare the panel, and complete a tiny local smoke run.
3. Compare short-lived self-hosted inference with managed access for the exact
   candidates. Retain likelihood scoring; models without candidate likelihoods
   need a separately labeled generated-answer track.
4. Price the complete pilot, including idle resources. Implement cloud runtime
   limits, a cumulative cost ledger, cleanup and concrete retrieval adapters.
   The current planner is **not a runtime spending cap**. Do not run this CLI on
   paid infrastructure assuming it can stop instance billing.
5. Run the bounded AWS pilot, then decide whether to spend the remaining budget.
6. Add offline scoring replay and paired uncertainty; reconcile costs. Publish
   reviewed compact summaries at a new `/part-ii/` path, keeping 2025 intact.

The public site is currently served by Netlify. The deployment command in
`../WEB_BUILD.md` is documentation, not independently verified account settings.
Do not push a production build or replace the homepage to preview this work.
