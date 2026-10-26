# Public blueprint v0.1

Published at `/part-ii/`. This supersedes the earlier broad PRD and the starter
pilot roster **as a proposal only**. It does not authorize experimentation.

The user authorized committing/pushing the blueprint and notes to the GitHub
repository that Netlify deploys. No model run, weight download, cloud resource
creation or paid experiment is authorized by that publication.

## Proposed decision

Interpret “several GB” as <=5 decimal GB of native weight files per contestant:

- `Qwen/Qwen3.5-0.8B-Base`: 1,746,942,600 bytes.
- `Qwen/Qwen3.5-2B-Base`: 4,548,221,488 bytes.
- `meta-llama/Llama-3.2-1B`: 2,471,645,608 bytes.

`models.json` records the publisher metadata and exact revisions checked on
2026-10-26. Files were enumerated through the Hugging Face API; weights were
not downloaded. These sizes exclude tokenizer/configuration, dependencies,
corpus/index and runtime memory. The Qwen packages include vision parameters;
only text will be evaluated. Base checkpoints preserve a shared plain-text
likelihood protocol. Post-trained variants remain an explicit alternative.

The original 3B base checkpoint is 6,425,529,048 bytes, outside the proposed
cap. Its 53.92% historical MMLU aggregate is not a 1B result. Keep the archive
and explain the discrepancy with the article; never silently relabel it.

## AWS proposal

One short-lived EC2 `g5.2xlarge` candidate (24 GiB A10G GPU / 32 GiB host RAM),
one model at a time, short context, no public inference API. Region us-west-2
is proposed. Validate compatibility, quota, capacity, runtime memory and a dated
price quote before launch. The original lm-eval 0.4.9.1 starter pin is not proof
of Qwen3.5 support; update and lock a validated environment before evaluation.

CloudFormation provisions scoped IAM, encrypted S3/EBS, SSM access, logging,
the worker and its expiry control. Proposed worker networking: temporary
public IPv4, no inbound rules, outbound HTTPS for artifacts/SSM; include IP
charges. No NAT gateway or persistent search cluster in the initial design.
Use local FAISS/BM25 retrieval and a small cross-encoder on the worker. The
post-trained Qwen0.8B sibling supplies frozen query rewrites, once per question.
Its compute and disk count toward cost even though it is not a contestant.

Gold labels are in a separate S3 prefix denied to the worker role. A separate
local scoring job uses a gold-reading role after the worker's predictions are
saved. The existing harness currently combines data/model/scoring locally;
implement this separation before claiming IAM-enforced label isolation.

Quality: shared precomputed retrieval evidence. Latency: separate uncached
subset. Archive immutable attempts and completion/failure status. Save reviewed
summary exports through GitHub to Netlify; no browser action invokes AWS.

## Scope and financial controls

Smoke: 5 MMLU development global-facts + 5 HellaSwag training items, disjoint
from the final panel, across 3 models x 3 arms = 90 scored answers.
Panel: 2 MMLU test items per subject (114) + 100 HellaSwag validation items =
214 shared questions, 1,926 scored answers, 7,704 candidate likelihoods.
This cannot establish precise subject rankings or tiny improvements.

Total ceiling $200, target $100. Proposed allocations: $20 smoke, $30 corpus/
retrieval preparation, $80 main panel, $30 analysis/reruns, $40 contingency.
These are envelopes, not price estimates. Compute, idle time, storage, IPs,
network, logs and retained artifacts all count. Price before provisioning.
Implement cumulative ledger, conservative batch reservation, maximum one
worker, two-hour initial lease, scheduled expiry and explicit cleanup. Billing
alerts alone cannot cap spend; retained resources still incur charges.

## Publication

`build_web_dashboard.py` keeps the existing dashboard generation and adds
this page. `index.template.html` is self-contained except for ordinary links;
`build.py` injects verified model sizes and copies the manifest. No model,
AWS SDK, credentials or experiment dependency is needed for a Netlify build.

```sh
python part2/blueprint/build.py --out part2/preview/blueprint
python build_web_dashboard.py
```

The old dashboard gains only a link. Historical JSON is not modified. The
blueprint is generated into `dist/part-ii/`, so it survives the existing build's
removal/recreation of `dist`. Do not hand-edit generated HTML.

Explicit approval of the model roster, architecture, compatibility and dated
cost estimate is required before any execution. No UI click records approval.
