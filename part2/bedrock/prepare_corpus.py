"""Prepare a deterministic, local-only S3 document sample. No AWS calls."""
import argparse
import hashlib
import json
import random
from pathlib import Path


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def render_document(row):
    return (f"{row['title']}\nSource: {row['url']}\n"
            "Snapshot: 20220301.simple\n"
            "License: CC BY-SA 3.0; attribution: Wikipedia contributors\n\n"
            f"{row['text']}\n").encode('utf-8')


def export_sample(rows, destination, count=1000, seed=20261026):
    if not 0 < count <= len(rows):
        raise ValueError('Sample size must be within the source row count')
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    documents = destination / 'documents'
    documents.mkdir()
    records = []
    for index in sorted(random.Random(seed).sample(range(len(rows)), count)):
        row = rows[index]
        content = render_document(row)
        # Dataset IDs and titles never become filesystem paths.
        name = f'article-{index:06d}.txt'
        (documents / name).write_bytes(content)
        records.append({'file': f'documents/{name}', 'source_row': index,
                        'article_id': row['id'], 'url': row['url'],
                        'bytes': len(content), 'sha256': sha256(content)})
    manifest = {'schema_version': 1, 'snapshot': '20220301.simple',
                'seed': seed, 'source_articles': len(rows), 'sample_articles': count,
                'purpose': 'Ingestion/retrieval plumbing smoke test; not a corpus coverage study',
                'source_bytes': sum(r['bytes'] for r in records),
                'documents': records}
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--count', type=int, default=1000)
    args = parser.parse_args()
    import pyarrow as pa
    source = args.dataset / 'train/data-00000-of-00001.arrow'
    info = json.loads((args.dataset / 'train/dataset_info.json').read_text())
    if info['config_name'] != '20220301.simple':
        raise ValueError('Unexpected corpus snapshot')
    table = pa.ipc.open_stream(pa.memory_map(str(source))).read_all()
    rows = table.to_pylist()
    manifest = export_sample(rows, args.out, args.count)
    full_bytes = sum(len(render_document(row)) for row in rows)
    summary = {key: value for key, value in manifest.items() if key != 'documents'}
    summary.update({'source_arrow_sha256': sha256(source.read_bytes()),
                    'full_export_estimated_bytes': full_bytes,
                    'full_export_storage_usd_per_month_at_5_per_gb': full_bytes/1e9*5,
                    'sample_storage_usd_per_month_at_5_per_gb': manifest['source_bytes']/1e9*5})
    (args.out / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
