import copy
import json
import tempfile
import unittest
from pathlib import Path
from tinybench.core import digest, historical_inventory, plan, select_samples, write_new
from tinybench.retrieval import question_stem, retrieve
from tinybench.report import render

CONFIG = json.loads((Path(__file__).parents[1] / 'configs/pilot.json').read_text())


class PlanningTests(unittest.TestCase):
    def test_counts_include_every_mmlu_subject(self):
        result = plan(CONFIG)
        self.assertEqual(result['scored_answers'], 1926)
        self.assertEqual(result['candidate_likelihood_evaluations'], 7704)
        self.assertIsNone(result['estimated_pilot_liability_usd'])
        self.assertTrue(result['launch_blockers'])

    def test_budget_and_unknown_costs_fail_closed(self):
        config = copy.deepcopy(CONFIG)
        config['budget']['project_ceiling_usd'] = 201
        with self.assertRaises(ValueError):
            plan(config)
        config = copy.deepcopy(CONFIG)
        config['cost_estimate'] = dict(compute_and_idle_usd=18, retrieval_usd=2,
            storage_network_usd=1, retry_allowance_usd=1, source='test', price_date='2026-10-26')
        self.assertTrue(any('exceeds' in s for s in plan(config)['launch_blockers']))
        config['cost_estimate']['compute_and_idle_usd'] = float('nan')
        with self.assertRaises(ValueError):
            plan(config)

    def test_sampling_is_paired_and_order_independent(self):
        sizes = {f'mmlu_subject_{i}': 100 for i in range(57)} | {'hellaswag': 10042}
        a = select_samples(sizes, CONFIG)
        b = select_samples(dict(reversed(list(sizes.items()))), CONFIG)
        self.assertEqual(a, b)
        self.assertEqual(sum(map(len, a.values())), 214)
        self.assertTrue(all(len(set(v)) == len(v) for v in a.values()))

    def test_historical_aggregate_is_not_relabelled_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'model/result.json'
            write_new(path, {'config': {'model_args': '3B'}, 'results': {'mmlu': {'acc,none': .5}},
                            'n-samples': {'mmlu_a': {'effective': 2}, 'mmlu_b': {'effective': 4}}})
            record = historical_inventory(Path(tmp))['runs'][0]
            self.assertEqual(record['metrics'][0]['n'], 6)
            self.assertIn('not verified', record['provenance'])
            with self.assertRaises(FileExistsError):
                write_new(path, {})


class RetrievalTests(unittest.TestCase):
    def test_baseline_never_calls_retrieval(self):
        def forbidden(*args):
            self.fail('Baseline accessed retrieval')
        self.assertEqual(retrieve('Q', 'none', forbidden, forbidden)['context'], '')

    def test_multiple_queries_dedupe_and_rerank_before_packing(self):
        calls = []
        def search(query, k):
            calls.append((query, k))
            return [{'id': 'a', 'text': 'same'}, {'id': 'duplicate', 'text': 'same'},
                    {'id': 'b', 'text': 'better evidence'}]
        def rerank(question, chunks):
            self.assertEqual({c['id'] for c in chunks}, {'a', 'b'})
            return ['b', 'a']
        result = retrieve('Q', 'multi_rerank', search, rerank, ['Q1', 'Q2', 'Q3'],
                          final_k=1, count_tokens=lambda text: len(text.split()))
        self.assertEqual(len(calls), 4)
        self.assertEqual(result['selected'], ['b'])
        self.assertEqual(result['excluded'], ['a'])

    def test_single_order_and_whole_chunk_budget(self):
        result = retrieve('Q', 'single', lambda *args: [{'id': 'b', 'text': 'long chunk here'},
            {'id': 'a', 'text': 'fits'}], None, token_budget=2, count_tokens=lambda s: len(s.split()))
        self.assertEqual(result['selected'], ['a'])
        self.assertEqual(result['context'], '[a] fits')

    def test_rewrite_and_rerank_validation(self):
        with self.assertRaises(ValueError):
            retrieve('Q', 'multi_rerank', None, None, ['Q', 'Q1', 'Q2'], count_tokens=len)
        with self.assertRaises(ValueError):
            retrieve('Q', 'multi_rerank', lambda *a: [{'id': 'a', 'text': 'x'}],
                     lambda *a: ['invented'], ['1','2','3'], count_tokens=len)

    def test_queries_exclude_choices_and_labels(self):
        self.assertEqual(question_stem('mmlu_global_facts', {'question': 'Q', 'choices': ['secret'], 'answer': 0}), 'Q')
        self.assertEqual(question_stem('hellaswag', {'ctx': 'Story', 'endings': ['secret'], 'label': '0'}), 'Story')


class ReportTests(unittest.TestCase):
    def test_empty_state_has_no_fabricated_scores(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'index.html'
            render(Path(tmp) / 'runs', output)
            self.assertIn('No completed experiments yet', output.read_text())

    def test_rejects_tampered_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_new(root/'runs/a/manifest.json', {})
            write_new(root/'runs/a/completion.json', {'results_sha256': digest({'old': True})})
            write_new(root/'runs/a/results.json', {'changed': True})
            with self.assertRaises(ValueError):
                render(root/'runs', root/'index.html')

    def test_production_output_is_protected(self):
        with self.assertRaises(ValueError):
            render('/nonexistent', Path(__file__).resolve().parents[2] / 'dist/index.html')


if __name__ == '__main__':
    unittest.main()
