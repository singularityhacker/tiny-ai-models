import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('prepare_corpus', Path(__file__).parents[1] / 'bedrock/prepare_corpus.py')
corpus = importlib.util.module_from_spec(spec)
spec.loader.exec_module(corpus)


class CorpusTests(unittest.TestCase):
    def test_sample_reproducibility_integrity_and_safe_names(self):
        rows = [{'id': '../escape', 'title': 'A title', 'url': 'https://example.org/a',
                 'text': f'Unicode text café {i}'} for i in range(20)]
        with tempfile.TemporaryDirectory() as root:
            a, b = Path(root)/'a', Path(root)/'b'
            first = corpus.export_sample(rows, a, 5)
            self.assertEqual(first, corpus.export_sample(rows, b, 5))
            self.assertEqual(len({d['source_row'] for d in first['documents']}), 5)
            for doc in first['documents']:
                data = (a/doc['file']).read_bytes()
                self.assertEqual(doc['sha256'], corpus.sha256(data))
                self.assertEqual(doc['bytes'], len(data))
                self.assertIn(b'CC BY-SA 3.0', data)
            self.assertFalse((Path(root)/'escape').exists())
            with self.assertRaises(FileExistsError):
                corpus.export_sample(rows, a, 5)

    def test_reject_invalid_sample_before_creating_directory(self):
        with tempfile.TemporaryDirectory() as root:
            target = Path(root)/'bad'
            for count in (0, -1, 2):
                with self.assertRaises(ValueError):
                    corpus.export_sample([{}], target, count)
            self.assertFalse(target.exists())
