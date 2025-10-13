# RAG Evaluation Usage Guide

## Quick Start

### 1. Test with Limited Examples (Recommended First Step)
```bash
python rag_eval.py \
  --model meta-llama/Llama-3.2-3B \
  --tasks mmlu_global_facts \
  --device mps \
  --limit 10
```

### 2. Full Evaluation
```bash
python rag_eval.py \
  --model meta-llama/Llama-3.2-3B \
  --tasks mmlu_global_facts \
  --device mps
```

## Comparing Baseline vs RAG

### Run Baseline Evaluation
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-3.2-3B \
  --tasks mmlu_global_facts \
  --output_path ./results/ \
  --device mps
```

### Run RAG Evaluation
```bash
python rag_eval.py \
  --model meta-llama/Llama-3.2-3B \
  --tasks mmlu_global_facts \
  --device mps
```

### View Results in Dashboard
```bash
cd dashboard
python server.py
```

The dashboard will show both models:
- `meta-llama__Llama-3.2-3B` - Baseline model
- `rag-meta-llama__Llama-3.2-3B` - RAG-enhanced model

## Advanced Options

### Adjust Number of Retrieved Chunks
```bash
# Default is 3, try 5 for more context
python rag_eval.py \
  --model meta-llama/Llama-3.2-3B \
  --tasks mmlu_global_facts \
  --device mps \
  --n_retrieval 5
```

### Different Tasks
```bash
# Try other MMLU subjects where Wikipedia might help
python rag_eval.py \
  --model meta-llama/Llama-3.2-3B \
  --tasks mmlu_world_religions \
  --device mps
```

### Custom ChromaDB Location
```bash
python rag_eval.py \
  --model meta-llama/Llama-3.2-3B \
  --tasks mmlu_global_facts \
  --device mps \
  --chroma_path /path/to/chroma_db
```

## Understanding the Results

### Retrieval Statistics
After each run, you'll see:
```
📊 Retrieval Statistics:
   Total retrievals performed: 40
```

This shows how many times the system queried Wikipedia (one per answer choice in multiple-choice questions).

### Performance Metrics
The results summary shows:
```
📈 Results Summary:
   mmlu_global_facts: 30.00%
```

Compare this with your baseline results to measure RAG improvement!

## How RAG Enhances Answers

For each question, the system:

1. **Extracts the question** from the MMLU prompt
2. **Searches Wikipedia** for the 3 most relevant chunks
3. **Augments the prompt** with context:
   ```
   Reference information from Wikipedia:
   [Article 1] relevant text...
   
   [Article 2] relevant text...
   
   [Article 3] relevant text...
   
   Based on the above information and your knowledge, answer the following:
   
   [Original MMLU question]
   ```
4. **Model answers** with enriched context

## Troubleshooting

### "No module named 'chromadb'"
Make sure you've activated the virtual environment:
```bash
source venv/bin/activate
```

### Out of Memory
Try reducing the number of retrieved chunks:
```bash
python rag_eval.py --n_retrieval 1 --limit 10
```

### Slow Performance
The RAG evaluation is slower than baseline because:
- It queries ChromaDB for each question
- Prompts are longer (includes retrieved context)

For testing, use `--limit` to evaluate fewer examples.

## Best Practices

1. **Start small**: Always test with `--limit 10` first
2. **Compare apples-to-apples**: Run baseline and RAG on the same tasks
3. **Experiment with retrieval**: Try different `--n_retrieval` values (1, 3, 5, 7)
4. **Check relevance**: Use `query_embeddings.py` to verify your knowledge base has relevant content
5. **Monitor resources**: RAG uses more memory due to longer prompts

## Results Storage

Results are automatically saved to:
```
./results/rag-{model-name}/{timestamp}.json
```

These files are compatible with your existing dashboard and can be compared directly with baseline results.

