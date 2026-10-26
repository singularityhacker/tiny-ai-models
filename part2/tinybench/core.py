"""Dependency-free planning, provenance, and deterministic panel selection."""
import hashlib
import json
import math
import random
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def file_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n')


def positive_int(value, name):
    if type(value) is not int or value <= 0:
        raise ValueError(f'{name} must be a positive integer')
    return value


def money(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f'{name} must be finite and nonnegative')
    return value


def plan(config):
    if config['schema_version'] != 1:
        raise ValueError('Unsupported config schema')
    models, arms, samples = config['models'], config['arms'], config['samples']
    if not models or len({m['id'] for m in models}) != len(models):
        raise ValueError('Models must have unique IDs')
    if not arms or len(set(arms)) != len(arms) or set(arms) - {'none', 'single', 'multi_rerank'}:
        raise ValueError('Invalid or duplicate retrieval arms')
    mmlu = positive_int(samples['mmlu_per_subject'], 'mmlu_per_subject') * positive_int(samples['mmlu_subjects'], 'mmlu_subjects')
    hs = positive_int(samples['hellaswag'], 'hellaswag')
    budget = config['budget']
    ceiling = money(budget['project_ceiling_usd'], 'project ceiling')
    pilot = money(budget['pilot_ceiling_usd'], 'pilot ceiling')
    reserve = money(budget['contingency_fraction'], 'contingency')
    if not 0 < pilot <= ceiling <= 200 or reserve < 0.2:
        raise ValueError('Require 0 < pilot <= project <= $200 and at least 20% contingency')
    blockers = [f"Pin checkpoint and revision for {m['id']}" for m in models if not m.get('checkpoint') or not m.get('revision')]
    estimate = config.get('cost_estimate')
    maximum = None
    if estimate is None:
        blockers.append('Price compute, retrieval, storage/network, and retries before paid execution')
    else:
        categories = ['compute_and_idle_usd', 'retrieval_usd', 'storage_network_usd', 'retry_allowance_usd']
        maximum = round(sum(money(estimate[k], k) for k in categories) * (1 + reserve), 4)
        if not estimate.get('price_date') or not estimate.get('source'):
            blockers.append('Cost estimate needs a price date and source')
        if maximum > pilot:
            blockers.append(f'Estimated pilot liability ${maximum:.2f} exceeds ${pilot:.2f}')
    count = (mmlu + hs) * len(models) * len(arms)
    return {'schema_version': 1, 'config_sha256': digest(config), 'protocol': config['protocol'],
            'items_per_model_arm': {'mmlu': mmlu, 'hellaswag': hs},
            'model_arm_cells': len(models) * len(arms), 'scored_answers': count,
            'candidate_likelihood_evaluations': count * 4,
            'estimated_pilot_liability_usd': maximum, 'budget': budget,
            'launch_blockers': blockers,
            'note': 'Likelihood evaluations are not generation API calls. This is a plan, not a spending guard or launch authorization.'}


def select_samples(task_sizes, config):
    """Stable per-task IDs; no dependence on task iteration order."""
    mmlu = sorted(t for t in task_sizes if t.startswith('mmlu_'))
    if len(mmlu) != config['samples']['mmlu_subjects'] or 'hellaswag' not in task_sizes:
        raise ValueError('Expected all declared MMLU subjects and HellaSwag')
    selected = {}
    for task in mmlu + ['hellaswag']:
        n = config['samples']['hellaswag' if task == 'hellaswag' else 'mmlu_per_subject']
        positive_int(n, task)
        if n > task_sizes[task]:
            raise ValueError(f'{task}: requested {n} of {task_sizes[task]} items')
        rng = random.Random(f"{config['seed']}:{task}")
        selected[task] = sorted(rng.sample(range(task_sizes[task]), n))
    return selected


def historical_inventory(root):
    records = []
    for path in sorted(Path(root).glob('*/*.json')):
        data = json.loads(path.read_text())
        config = data.get('config', {})
        metrics = []
        for task, values in data.get('results', {}).items():
            if task not in {'mmlu', 'hellaswag', 'mmlu_global_facts'}:
                continue
            n = data.get('n-samples', {}).get(task, {}).get('effective')
            if task == 'mmlu':
                n = sum(v['effective'] for k, v in data.get('n-samples', {}).items() if k.startswith('mmlu_'))
            for metric in ('acc,none', 'acc_norm,none'):
                if metric in values:
                    metrics.append({'task': task, 'metric': metric, 'value': values[metric], 'n': n})
        records.append({'path': str(path.relative_to(root)), 'sha256': file_digest(path),
                        'model_args': config.get('model_args'), 'model_sha': config.get('model_sha'),
                        'limit': config.get('limit'), 'harness_version': data.get('lm_eval_version'),
                        'metrics': metrics, 'provenance': 'historical aggregate; item-level replay not verified'})
    return {'schema_version': 1, 'runs': records}
