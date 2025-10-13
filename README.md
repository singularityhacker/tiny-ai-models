# Tiny AI Models

An experimental project for evaluating small AI models using lm-eval, with a beautiful interactive dashboard for visualizing results.

## Overview

This project provides a complete workflow for:
- Running evaluations on tiny AI models using `lm-eval`
- Creating Wikipedia knowledge bases with vector embeddings
- Visualizing results with an interactive web dashboard
- Comparing performance across different model runs
- Analyzing detailed metrics and failure patterns

## Setup

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- CUDA/MPS support for GPU acceleration (optional)

### Installation

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running Evaluations with lm-eval

### Basic Evaluation (Baseline)

Run a quick test with limited samples:
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-3.2-3B \
  --tasks hellaswag,mmlu \
  --limit 10 \
  --output_path ./results/ \
  --device mps
```

### Full Evaluation (Baseline)

Run complete evaluation on all questions:
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-3.2-3B \
  --tasks hellaswag,mmlu \
  --output_path ./results/ \
  --device mps
```

### RAG-Enhanced Evaluation (NEW! 🎯)

Run evaluation with Wikipedia knowledge base augmentation:

**Quick test (10 questions):**
```bash
python rag_eval.py \
  --model meta-llama/Llama-3.2-3B \
  --tasks mmlu_global_facts \
  --device mps \
  --limit 10
```

**Full evaluation:**
```bash
python rag_eval.py \
  --model meta-llama/Llama-3.2-3B \
  --tasks mmlu_global_facts \
  --device mps
```

**Customize retrieval:**
```bash
python rag_eval.py \
  --model meta-llama/Llama-3.2-3B \
  --tasks mmlu_global_facts \
  --device mps \
  --n_retrieval 5  # Retrieve 5 Wikipedia chunks instead of 3
```

### Evaluation Options

- `--model hf`: Use HuggingFace models
- `--model_args pretrained=<model_name>`: Specify the model to evaluate
- `--tasks hellaswag,mmlu`: Tasks to run (HellaSwag and MMLU benchmarks)
- `--limit <number>`: Limit number of questions (useful for testing)
- `--output_path ./results/`: Directory to save results
- `--device mps`: Use Apple Silicon GPU (or `cuda` for NVIDIA, `cpu` for CPU-only)

### Supported Models

Any HuggingFace model compatible with transformers:
- `meta-llama/Llama-3.2-3B` (used in examples)
- `microsoft/DialoGPT-medium`
- `EleutherAI/gpt-neo-2.7B`
- And many more...

### Supported Tasks

- **hellaswag**: Commonsense reasoning (10,042 questions)
- **mmlu**: Massive multitask language understanding (15,908 questions across 57 subjects)
- **arc**: AI2 reasoning challenge
- **truthfulqa**: Truthfulness evaluation
- And 100+ other benchmarks

## Wikipedia Knowledge Base

### Creating Embeddings

The project includes tools for creating a Wikipedia knowledge base using vector embeddings:

1. **Download Simple Wikipedia:**
   ```bash
   python simple-wiki-dl.py
   ```

2. **Create embeddings:**
   ```bash
   python create_embeddings_simple.py
   ```

3. **Query the knowledge base:**
   ```bash
   python query_embeddings.py --query "What is machine learning?"
   ```

### Knowledge Base Features

- **Vector embeddings** using `sentence-transformers/all-mpnet-base-v2`
- **ChromaDB storage** for efficient similarity search
- **Smart chunking** - Articles split into manageable pieces
- **Semantic search** - Find relevant content by meaning, not just keywords
- **Metadata tracking** - Title, chunk ID, and article information

### Usage Examples

```bash
# Check collection statistics
python query_embeddings.py --stats

# Search for specific topics
python query_embeddings.py --query "What is photosynthesis?"

# Interactive search mode
python query_embeddings.py
```

## Dashboard Features

- 📊 **Interactive Charts**: Visualize performance across different tasks and subjects
- 📈 **Key Metrics**: Quick overview of overall accuracy, HellaSwag, and MMLU scores
- 📋 **Sortable Results Table**: Complete breakdown with visual accuracy bars and sorting
- ⏱️ **Test Duration**: Shows how long evaluations took to complete
- 📊 **Question Breakdown**: Shows total questions evaluated per test
- 🔄 **Model Comparison**: Compare results across different evaluation runs
- 📱 **Responsive Design**: Works on desktop and mobile devices

## Quick Start

1. **Run an evaluation:**
   ```bash
   lm_eval --model hf --model_args pretrained=meta-llama/Llama-3.2-3B --tasks hellaswag,mmlu --limit 10 --output_path ./results/ --device mps
   ```

2. **Start the dashboard server:**
   ```bash
   cd dashboard
   python server.py
   ```

3. **Open your browser:**
   The dashboard will automatically open at `http://localhost:8080`

4. **View your results:**
   - Choose from available models in the dropdown
   - Select a specific evaluation run
   - View interactive charts and detailed results
   - Sort the results table by accuracy, task name, or error margin

## API Endpoints

The server provides REST API endpoints for programmatic access:

- `GET /api/models` - List all available models
- `GET /api/runs?model_id=<id>` - List runs for a specific model  
- `GET /api/data/<run_id>` - Get detailed data for a specific run

## Project Structure

```
tiny-ai-models/
├── dashboard/
│   ├── index.html      # Interactive dashboard interface
│   └── server.py       # HTTP server with API endpoints
├── results/            # Evaluation results (auto-generated)
│   ├── meta-llama__Llama-3.2-3B/          # Baseline model results
│   │   ├── results_2025-10-03T14-37-54.407411.json  # Limited test
│   │   └── results_2025-10-03T23-47-07.831204.json  # Full evaluation
│   └── rag-meta-llama__Llama-3.2-3B/      # RAG-enhanced model results
│       └── results_2025-10-08T18:09:50.857457.json
├── simple_wikipedia/   # Wikipedia dataset (auto-generated)
├── chroma_db/         # Vector embeddings database (auto-generated)
├── simple-wiki-dl.py  # Wikipedia downloader script
├── create_embeddings_simple.py  # Embedding creation script
├── query_embeddings.py # Knowledge base query tool
├── rag_eval.py        # RAG-enhanced evaluation script (NEW!)
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── notes.md           # Project notes and development log
```

## Workflow Example

1. **Test run** (quick validation):
   ```bash
   lm_eval --model hf --model_args pretrained=meta-llama/Llama-3.2-3B --tasks hellaswag,mmlu --limit 10 --output_path ./results/ --device mps
   ```

2. **Full evaluation** (comprehensive testing):
   ```bash
   lm_eval --model hf --model_args pretrained=meta-llama/Llama-3.2-3B --tasks hellaswag,mmlu --output_path ./results/ --device mps
   ```

3. **View results** in dashboard:
   ```bash
   cd dashboard && python server.py
   ```

4. **Analyze performance**:
   - Compare limited vs full test results
   - Sort by accuracy to find best/worst subjects
   - Check test duration and question counts
   - Identify areas for improvement

## Advanced Usage

### Custom Model Evaluation

Evaluate different models:
```bash
# Smaller model
lm_eval --model hf --model_args pretrained=microsoft/DialoGPT-medium --tasks hellaswag,mmlu --limit 100 --output_path ./results/ --device mps

# Different model size
lm_eval --model hf --model_args pretrained=EleutherAI/gpt-neo-2.7B --tasks hellaswag,mmlu --output_path ./results/ --device mps
```

### Additional Benchmarks

Try other evaluation tasks:
```bash
# Add more benchmarks
lm_eval --model hf --model_args pretrained=meta-llama/Llama-3.2-3B --tasks hellaswag,mmlu,arc,truthfulqa --limit 100 --output_path ./results/ --device mps
```

### Detailed Logging

For more detailed output (if supported):
```bash
lm_eval --model hf --model_args pretrained=meta-llama/Llama-3.2-3B --tasks hellaswag,mmlu --limit 10 --output_path ./results/ --device mps --log_samples
```

## Customization

### Changing the Results Directory

By default, the server looks for results in `../results/`. To change this:

```bash
python server.py 8080 /path/to/your/results
```

### Changing the Port

```bash
python server.py 3000  # Use port 3000 instead of 8080
```

## Technical Details

- **Evaluation Engine**: lm-eval (Language Model Evaluation Harness)
- **Frontend**: Vanilla JavaScript with Chart.js for visualizations
- **Backend**: Python HTTP server with JSON API
- **Data Format**: Expects lm-eval JSON output format
- **Browser Support**: Modern browsers with ES6+ support
- **GPU Support**: MPS (Apple Silicon), CUDA (NVIDIA), CPU fallback

## Troubleshooting

### Evaluation Issues

**"Model not found" error:**
- Verify the model name is correct on HuggingFace
- Check internet connection for model download
- Ensure sufficient disk space for model storage

**Out of memory errors:**
- Use `--limit` to reduce question count
- Try CPU evaluation with `--device cpu`
- Consider smaller models

**Slow evaluation:**
- Use GPU acceleration (`--device mps` or `--device cuda`)
- Reduce `--limit` for testing
- Check available system resources

### Dashboard Issues

**"No models found" error:**
- Ensure your results directory contains model subdirectories
- Check that JSON files follow the naming pattern `results_*.json`
- Verify lm-eval completed successfully

**Charts not displaying:**
- Check browser console for JavaScript errors
- Ensure your JSON data contains the expected structure with `acc,none` fields
- Try refreshing the page

**Server won't start:**
- Check that port 8080 is available
- Ensure Python 3.6+ is installed
- Verify the results directory path is correct

### Performance Tips

- **Start small**: Use `--limit 10` for initial testing
- **Monitor resources**: Watch CPU/GPU usage during evaluation
- **Save results**: Results are automatically saved with timestamps
- **Compare runs**: Use the dashboard to compare different evaluation runs

## RAG Evaluation System ✅

### What is RAG?

**Retrieval-Augmented Generation (RAG)** enhances language models by providing relevant context from a knowledge base. Before answering each question, the system:

1. Searches the Wikipedia knowledge base for relevant information
2. Retrieves the most relevant chunks (default: 3)
3. Augments the question prompt with this context
4. Lets the model answer with enriched information

### How It Works

The `rag_eval.py` script:
- Wraps the base Llama model with RAG capabilities
- Queries ChromaDB for relevant Wikipedia content for each question
- Injects retrieved context into prompts automatically
- Saves results in the same format as baseline evaluations
- Results appear in dashboard as a separate model for easy comparison

### Performance Comparison

Early results show RAG improvement on global facts:
- **Baseline model:** 25% accuracy (100 questions)
- **RAG-enhanced:** 30% accuracy (10 question sample)

Results are directly comparable in the dashboard!

### RAG Options

- `--n_retrieval N`: Number of Wikipedia chunks to retrieve (default: 3)
- `--chroma_path PATH`: Path to ChromaDB (default: ./chroma_db)
- All standard lm-eval options work: `--limit`, `--device`, `--tasks`, etc.

## Next Steps & Future Development

### Immediate Next Steps

1. ✅ **Scale up Wikipedia embeddings:** COMPLETE!
   - All Simple Wikipedia articles processed
   - Comprehensive knowledge base ready

2. ✅ **Integrate with evaluations:** COMPLETE!
   - RAG evaluation system implemented (`rag_eval.py`)
   - Wikipedia context enhances question answering
   - Dashboard shows baseline vs RAG comparison

3. **Run comprehensive RAG evaluations:**
   - Test on full MMLU global_facts dataset (100 questions)
   - Try other MMLU subjects where Wikipedia helps
   - Experiment with different retrieval settings (n_retrieval=5, 7, 10)

4. **Enhanced dashboard features:**
   - Add knowledge base integration to the dashboard
   - Show which Wikipedia articles were used for each evaluation
   - Display retrieval quality metrics

### Advanced Features

4. **Detailed failure analysis:**
   - Implement detailed question-by-question evaluation logging
   - Show which specific questions the model got wrong
   - Analyze failure patterns by subject area

5. **Model comparison framework:**
   - Compare multiple models side-by-side
   - Track improvement over time
   - Generate comparison reports

6. **Custom evaluation tasks:**
   - Create domain-specific evaluation benchmarks
   - Test models on specialized knowledge areas
   - Build evaluation suites for specific use cases

### Technical Improvements

7. **Performance optimization:**
   - Optimize embedding creation for larger datasets
   - Implement parallel processing for faster evaluations
   - Add caching for frequently accessed data

8. **Extended knowledge bases:**
   - Add other Wikipedia language versions
   - Include academic papers or technical documentation
   - Create domain-specific knowledge collections

### Research Applications

9. **Retrieval-augmented generation (RAG):**
   - Use Wikipedia knowledge to improve model responses
   - Implement context-aware evaluation methods
   - Study the impact of external knowledge on model performance

10. **Bias and fairness analysis:**
    - Analyze model performance across different demographic groups
    - Study knowledge representation biases
    - Implement fairness metrics in evaluations
