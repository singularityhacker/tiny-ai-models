"""Small, separate HTML report. Never writes to the production dist directory."""
import html
import json
from pathlib import Path
from .core import digest


def render(runs_dir, output):
    rows = []
    for folder in sorted(Path(runs_dir).glob('*')):
        if not (folder / 'completion.json').exists():
            continue
        manifest = json.loads((folder / 'manifest.json').read_text())
        completion = json.loads((folder / 'completion.json').read_text())
        result = json.loads((folder / 'results.json').read_text())
        if completion['results_sha256'] != digest(result):
            raise ValueError(f'Result checksum mismatch: {folder}')
        for task in ('mmlu', 'hellaswag'):
            metrics = result.get('results', {}).get(task, {})
            samples = result.get('n-samples', {})
            n = samples.get(task, {}).get('effective')
            if task == 'mmlu':
                n = sum(v['effective'] for k, v in samples.items() if k.startswith('mmlu_'))
            for metric in ('acc,none', 'acc_norm,none'):
                if metric not in metrics:
                    continue
                values = [folder.name, manifest['model']['id'], manifest['arm'], task,
                          metric, str(n), f'{metrics[metric] * 100:.2f}%',
                          manifest['panel_sha256'][:12], 'Not measured']
                rows.append('<tr>' + ''.join(f'<td>{html.escape(v)}</td>' for v in values) + '</tr>')
    body = ('<div class="scroll"><table><thead><tr>' + ''.join(f'<th>{h}</th>' for h in
            ['Run', 'Model', 'Retrieval', 'Benchmark', 'Metric', 'Questions', 'Accuracy', 'Panel', 'Cost']) +
            '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>') if rows else (
            '<section><h2>No completed experiments yet</h2><p>The pilot is being prepared. '
            'Results will appear here after real benchmark runs finish. No illustrative scores are shown.</p></section>')
    page = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tiny Models — Part II pilot</title><style>
body{margin:0;background:#0b1220;color:#f3f6fa;font:16px/1.6 system-ui,sans-serif}
main{max-width:1200px;margin:64px auto;padding:0 24px}a{color:#41d9ec}
.eyebrow{color:#c4ef67;letter-spacing:.12em;text-transform:uppercase;font-size:13px}
h1{font-size:clamp(32px,6vw,56px);line-height:1.1}p{max-width:760px;color:#b7c6d9}
section{background:#142238;border:1px solid #34455d;border-radius:12px;padding:24px;margin:32px 0}
.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:12px;border-bottom:1px solid #34455d;white-space:nowrap}
a:focus-visible{outline:3px solid #c4ef67;outline-offset:4px}
</style><main><div class="eyebrow">Part II / experimental preview</div>
<h1>How far can a tiny model go?</h1>
<p>MMLU and HellaSwag, revisited with smaller current models and multiple searches followed by reranking. Pilot results are exploratory subsets, not full benchmark claims.</p>
<p><a href="https://evals.justiceconder.com/">Visit the original 2025 dashboard ↗</a></p>
''' + body + '''<section><h2>Reading the results</h2><p>Compare runs only when their panel hashes and protocols match. MMLU accuracy and HellaSwag raw / length-normalized accuracy stay separate. Cached evidence measures answer quality; these runs do not measure end-to-end retrieval latency. Costs remain “not measured” until reconciled.</p></section></main></html>'''
    output = Path(output).resolve()
    production = Path(__file__).resolve().parents[2] / 'dist'
    if output == production or production in output.parents:
        raise ValueError('Preview report cannot write into production dist/')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page)
