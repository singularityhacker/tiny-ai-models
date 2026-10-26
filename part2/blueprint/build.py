"""Build the public proposal from checked model metadata; never run experiments."""
import html
import json
from pathlib import Path


def build_blueprint(destination):
    source = Path(__file__).resolve().parent
    manifest = json.loads((source / 'models.json').read_text())
    models = {m['id']: m for m in manifest['models']}
    selected = [
        ('Qwen/Qwen3.5-0.8B-Base', '01 / Current · smallest', 'Qwen3.5 0.8B Base',
         'The smallest current candidate. Tests how much a better library can compensate for a very small model.'),
        ('Qwen/Qwen3.5-2B-Base', '02 / Current · more capacity', 'Qwen3.5 2B Base',
         'A larger sibling, still under 5 GB in native precision. Tests the quality gained by spending a few more gigabytes.'),
        ('meta-llama/Llama-3.2-1B', '03 / Historical-era comparator', 'Llama 3.2 1B',
         'A compact 2024 base model. A new comparator for this study; the recovered 2025 score belongs to the 3B model.')]
    cards = []
    for mid, tag, title, rationale in selected:
        model = models[mid]
        size = model['weight_bytes']
        if not 0 < size <= 5_000_000_000:
            raise ValueError(f'Proposed contestant exceeds weight cap: {mid}')
        params = model['safetensors_parameters']['total'] / 1e9
        cards.append(f'''<article class="card"><span class="tag">{tag}</span>
<h3>{title}</h3><div class="size" data-bytes="{size}">{size/1e9:.2f} GB</div>
<small>Native weight files · {params:.3f}B stored parameters</small><p>{rationale}</p>
<small>License: {html.escape(model['license'])}</small>
<a href="{model['source']}/tree/{model['revision']}">Inspect pinned files ↗</a>
<small>Revision <code>{model['revision'][:12]}</code></small></article>''')
    alternatives = [
        ('Qwen/Qwen3.5-0.8B', 'Qwen3.5 0.8B post-trained', 'Same size; proposed rewrite helper. Chat evaluation would be a separate track.'),
        ('Qwen/Qwen3.5-2B', 'Qwen3.5 2B post-trained', 'Same size; alternative if instruction-following is the primary question.'),
        ('google/gemma-3-1b-it', 'Gemma 3 1B IT', 'Fits; useful family-diversity alternative, but predates Part I and is instruction-tuned.'),
        ('HuggingFaceTB/SmolLM3-3B', 'SmolLM3 3B', '6.15 GB native weights; outside the proposed cap and released before Part I.'),
        ('google/gemma-4-E2B-it', 'Gemma 4 E2B', '10.25 GB native weights; “effective” parameter count understates the stored model.'),
        ('meta-llama/Llama-3.2-3B', 'Llama 3.2 3B', 'Original recovered checkpoint. Preserve its archive; rerunning needs a size exception.')]
    rows = []
    for mid, label, decision in alternatives:
        model = models[mid]
        rows.append(f'<tr><td><a href="{model["source"]}/tree/{model["revision"]}">{label}</a></td>'
                    f'<td data-bytes="{model["weight_bytes"]}">{model["weight_bytes"]/1e9:.2f} GB</td>'
                    f'<td>{html.escape(decision)}</td></tr>')
    page = (source / 'index.template.html').read_text()
    page = page.replace('__MODEL_CARDS__', '\n'.join(cards)).replace('__ALTERNATIVE_ROWS__', '\n'.join(rows))
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'index.html').write_text(page)
    (destination / 'models.json').write_text((source / 'models.json').read_text())


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='part2/preview/blueprint')
    build_blueprint(parser.parse_args().out)
