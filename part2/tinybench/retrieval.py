"""Provider-independent retrieval with explicit, reusable evidence traces."""
from .core import digest


def question_stem(task, doc):
    # Do not derive searches from formatted prompts, answer choices, or gold labels.
    if task.startswith('mmlu_'):
        return doc['question']
    if task == 'hellaswag':
        return doc['ctx']
    raise ValueError(f'Unsupported benchmark: {task}')


def retrieve(question, arm, search, rerank, variants=(), *, candidates=20,
             final_k=3, token_budget=1536, count_tokens=None):
    """search(query,k)->chunks; rerank(question,chunks)->ordered chunk IDs.

    Chunks have id/text. Token counting is mandatory for RAG. Variants are
    frozen upstream, shared across models; no hidden rewriting/model calls.
    """
    if arm not in {'none', 'single', 'multi_rerank'}:
        raise ValueError('Unknown retrieval arm')
    if arm == 'none':
        return {'arm': arm, 'queries': [], 'candidates': [], 'selected': [], 'context': ''}
    if count_tokens is None or min(candidates, final_k, token_budget) <= 0:
        raise ValueError('RAG requires a tokenizer and positive retrieval limits')
    queries = [question]
    if arm == 'multi_rerank':
        if len(variants) != 3 or len(set([question, *variants])) != 4 or not all(v.strip() for v in variants):
            raise ValueError('multi_rerank requires three distinct frozen query variants')
        queries += list(variants)
    traces, chunks, by_text, scores = [], {}, {}, {}
    for query in queries:
        result = search(query, final_k if arm == 'single' else candidates)
        traces.append({'query': query, 'results': result})
        seen = set()
        for rank, chunk in enumerate(result, 1):
            cid, text = chunk['id'], chunk['text']
            text_hash = digest(' '.join(text.split()))
            if cid in chunks and chunks[cid]['text'] != text:
                raise ValueError('Conflicting text for a chunk ID')
            canonical = by_text.setdefault(text_hash, cid)
            chunks.setdefault(canonical, chunk)
            if canonical not in seen:
                scores[canonical] = scores.get(canonical, 0) + 1 / (60 + rank)
                seen.add(canonical)
    ordered = sorted(chunks, key=lambda cid: (-scores[cid], cid))
    if arm == 'single':
        ordered = list(chunks)  # Preserve original search order.
    if arm == 'multi_rerank' and ordered:
        reranked = rerank(question, [chunks[cid] for cid in ordered])
        if len(reranked) != len(ordered) or set(reranked) != set(ordered):
            raise ValueError('Reranker must return every candidate ID exactly once')
        ordered = reranked
    selected, excluded, context = [], [], ''
    for cid in ordered:
        piece = f"[{cid}] {chunks[cid]['text']}"
        proposed = '\n\n'.join(filter(None, [context, piece]))
        if len(selected) >= final_k or count_tokens(proposed) > token_budget:
            excluded.append(cid)
        else:
            selected.append(cid)
            context = proposed
    return {'arm': arm, 'queries': queries, 'candidates': traces,
            'fusion_scores': scores, 'ranked_ids': ordered, 'selected': selected,
            'excluded': excluded, 'context': context, 'context_sha256': digest(context)}
