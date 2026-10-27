# Bedrock pilot preflight

The user approved the v0.2 Bedrock direction and the next step. The $20 pilot
and $200 total ceilings remain. `configs/bedrock.json` records that approval
separately from execution readiness; the legacy likelihood config stays disabled.

## Verified preflight

- Connected AWS tool authenticated to the previously selected project account.
- `GetFoundationModelAvailability`, us-west-2, for
  `mistral.ministral-3-3b-instruct`: agreement AVAILABLE, authorization AUTHORIZED,
  entitlement AVAILABLE, region AVAILABLE. No model invocation performed.
- `ListKnowledgeBases` failed with AccessDeniedException: explicit deny in an
  AWS Organizations service control policy. This is a cloud authorization
  response, not a local credential-refresh or automatic tool approval failure.
- No cloud resources created, corpus uploaded, or paid model requests sent.

An organization administrator must review the applicable service control policy
and authorize the project's Knowledge Base operations before setup can proceed.
An IAM Allow on the execution role cannot override this explicit deny. Do not
switch identities/regions or change organization policies to bypass the denial.
The failed list call establishes that action is denied; it does not establish
that every Bedrock API is denied. Creation and retrieval remain untested.

Account IDs, role ARNs and organization policy identifiers are intentionally
omitted from this public repository.

## Local corpus preparation

`prepare_corpus.py` reads the existing Arrow dataset without downloading models
or making AWS calls. It exports 1,000 deterministically sampled articles for
an ingestion/retrieval plumbing check, with source URLs and license attribution.
Names are based on row indices, not untrusted article titles or IDs. It refuses
to overwrite an existing export. Every document has a byte count and SHA-256.
The source snapshot is `20220301.simple`; `corpus-summary.json` records its hash.

```sh
venv/bin/python part2/bedrock/prepare_corpus.py \
  --dataset simple_wikipedia \
  --out part2/artifacts/bedrock-corpus-smoke-v1
PYTHONPATH=part2 python -m unittest discover -s part2/tests -q
```

The local export is ignored by Git. This sample is not suitable for claiming
benchmark corpus coverage; no sample was selected using benchmark gold labels.
Exporting all 205,328 articles in the same format would produce 250,489,331 bytes
(about 250 MB), including attribution/source headers. At the verified $5 per raw
GB-month rate, that is approximately $1.25/month. The 1,000-article sample is
1,141,946 bytes, approximately $0.006/month before any billing granularity.
These are storage illustrations only: S3 requests, retrieval, explicit rerank,
generation, judges, logs and retention must be included in the launch ledger.

## Resume after policy resolution

1. Repeat read-only Knowledge Base preflight in the same account/region.
2. Complete bounded request/usage accounting and pin the disjoint 10-question
   development smoke panel. Finalize a separate grounded-QA evaluation judge.
3. Create scoped IAM/S3 and a managed Knowledge Base, then upload and sync the
   small corpus sample. Verify retrieval before expanding the corpus.
4. Run the bounded smoke with capped output, retries and concurrency; preserve
   failures and traces. This is a plumbing check, not reported benchmark quality.
5. Reconcile spend and clean up retained resources. Freeze the full corpus and
   final study panel before the main experiment.

The public website remains the published v0.2 proposal. No experimental results
are available to add to its dashboard yet.
