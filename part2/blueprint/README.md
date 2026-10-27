# Public blueprint v0.2 — Bedrock

Published at `/part-ii/`. This supersedes v0.1 and the starter pilot roster
as a proposal only. Publication is authorized; experiments and provisioning
require explicit approval. No Bedrock adapters or infrastructure are deployed.

## Model requirement and evidence

The proposed definition is at most 5 decimal GB of published portable weights,
including an explicitly identified quantized artifact. This replaces the earlier
native/BF16 policy. Bedrock serving precision and memory are unknown.

Ministral 3 3B Instruct is ACTIVE / ON_DEMAND in the us-west-2 catalog.
Its publisher FP8 artifact is 4,672,099,184 bytes, with approximately 3.8B total
parameters including vision. `bedrock-evidence.json` records the pinned revision,
regional catalog subset, sources and cost arithmetic. Account access remains
untested: the entitlement read encountered a credential-refresh error.

Only one candidate is qualified under this portable-artifact interpretation.
The public page documents excluded/uncertain alternatives. Review must choose
one-model retrieval research or waiting for a second verified tiny candidate.
A one-model study cannot rank the best tiny models. No larger substitute or
self-hosted fallback is automatically authorized.

## Proposed experiment

- Bedrock Converse for generation; S3 corpus and Bedrock Managed Knowledge Base.
- N0: no retrieval. H3: one hybrid search, reranking off, top three chunks.
- MQHR3: original query plus three frozen Ministral rewrites; four hybrid
  searches of up to 20 chunks; deduplicate, reciprocal-rank fusion, explicit
  Bedrock Cohere Rerank 3.5, top three chunks. Shared 1,536-token evidence cap.
- Use `managedSearchConfiguration` for managed KB retrieval. Region and
  configuration support must pass preflight before provisioning.
- 114 MMLU + 100 HellaSwag questions, generated A/B/C/D accuracy: 642 answers
  for one model across three arms. No Part I comparability claim.
- Separate 30-item development grounded-QA audit across two RAG arms, with
  saved responses evaluated by Bedrock Evaluations. Judge is disclosed
  auxiliary infrastructure, not a tiny contestant.
- First smoke: ten disjoint development items, 30 answers for one model.

Freeze corpus and prompts; exclude gold labels from generator access; record
retrieval traces, failures, usage and versions. Publish paired uncertainty and
actual costs. Existing local likelihood tools are legacy scaffolding, not
implementation of this proposal.

## Financial controls

$200 total ceiling, target $100 or less, initial approved pilot at most $20.
Published rates checked 2026-10-26 give a $6.63 illustrative subtotal for 642
answers at assumed 2,000 input/16 output tokens, 1 GB-month managed KB storage,
1,070 retrieves and 214 single-unit explicit reranks. This excludes rewrites,
QA generation, judges, retries, S3, logs, tax and corpus expansion; it is not a
complete campaign quote. Reprice before launch.

Implement conservative call/retry reservations, concurrency/token limits,
cumulative ledger and retained-resource cleanup before execution. Billing
alerts alone cannot cap spending. Managed KB availability, account entitlement,
judge selection and full cost estimate remain launch gates.

## Publication

`build_web_dashboard.py` generates the historical dashboard and this separate
page. `build.py` copies the self-contained template, evidence and v0.1 archive.
`models.json` is retained only for historical compatibility, not the current
Bedrock roster. The old dashboard data stays unchanged.

```sh
python part2/blueprint/build.py --out part2/preview/blueprint
python build_web_dashboard.py
```

No model, AWS SDK, credentials or experiment dependency is needed to build.
The public review page has no execution controls.
