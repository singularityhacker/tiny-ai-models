#!/usr/bin/env python3
"""
RAG-Enhanced Model Evaluation

Runs lm-eval with Wikipedia knowledge base augmentation.
Results are compatible with the existing dashboard.
"""

import chromadb
from lm_eval import evaluator
from lm_eval.models.huggingface import HFLM
import json
import os
from datetime import datetime
from dataclasses import replace


class RAGAugmentedModel(HFLM):
    """
    Wrapper around HuggingFace model that augments prompts with Wikipedia context.
    """
    
    def __init__(self, 
                 pretrained: str,
                 chroma_path: str = "./chroma_db",
                 collection_name: str = "simple_wikipedia",
                 n_retrieval: int = 3,
                 **kwargs):
        """
        Initialize RAG-enhanced model.
        
        Args:
            pretrained: HuggingFace model name
            chroma_path: Path to ChromaDB database
            collection_name: ChromaDB collection name
            n_retrieval: Number of Wikipedia chunks to retrieve
            **kwargs: Additional arguments for HFLM
        """
        # Initialize parent HuggingFace model
        super().__init__(pretrained=pretrained, **kwargs)
        
        # Initialize ChromaDB for retrieval
        print(f"🔍 Loading Wikipedia knowledge base from {chroma_path}...")
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.chroma_client.get_collection(collection_name)
        self.n_retrieval = n_retrieval
        
        # Stats tracking
        self.retrieval_count = 0
        
        print(f"✅ RAG-enhanced model ready!")
        print(f"   Base model: {pretrained}")
        print(f"   Knowledge base: {collection_name}")
        print(f"   Retrieval chunks: {n_retrieval}")
    
    def _extract_question(self, context: str) -> str:
        """
        Extract the actual question from the prompt context.
        MMLU format typically has the question at the start.
        """
        # For MMLU, the question is usually before the choices
        # We'll use the full context for retrieval
        lines = context.strip().split('\n')
        
        # Try to find the question (usually first substantial line)
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('A.', 'B.', 'C.', 'D.', 'Answer:')):
                return line
        
        # Fallback to first 200 chars
        return context[:200]
    
    def _retrieve_context(self, question: str) -> str:
        """
        Retrieve relevant Wikipedia context for a question.
        """
        try:
            results = self.collection.query(
                query_texts=[question],
                n_results=self.n_retrieval
            )
            
            if not results['documents'][0]:
                return ""
            
            # Format retrieved context
            context_parts = []
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                title = metadata.get('title', 'Unknown')
                # Truncate long documents
                doc_preview = doc[:300] + "..." if len(doc) > 300 else doc
                context_parts.append(f"[{title}] {doc_preview}")
            
            context = "\n\n".join(context_parts)
            self.retrieval_count += 1
            
            return context
            
        except Exception as e:
            print(f"⚠️  Retrieval error: {e}")
            return ""
    
    def _augment_context(self, original_context: str) -> str:
        """
        Augment the original context with Wikipedia knowledge.
        """
        # Extract question
        question = self._extract_question(original_context)
        
        # Retrieve Wikipedia context
        wiki_context = self._retrieve_context(question)
        
        if not wiki_context:
            return original_context
        
        # Create augmented prompt
        augmented = f"""Reference information from Wikipedia:
{wiki_context}

Based on the above information and your knowledge, answer the following:

{original_context}"""
        
        return augmented
    
    def loglikelihood(self, requests):
        """
        Override loglikelihood to augment contexts with Wikipedia knowledge.
        This is called for multiple-choice tasks like MMLU.
        """
        # Augment all requests
        augmented_requests = []
        for req in requests:
            # Request is an Instance object with args attribute
            context, continuation = req.args
            augmented_context = self._augment_context(context)
            
            # Create new request with augmented context using dataclasses.replace
            new_req = replace(req, arguments=(augmented_context, continuation))
            augmented_requests.append(new_req)
        
        # Call parent implementation with augmented requests
        return super().loglikelihood(augmented_requests)
    
    def generate_until(self, requests):
        """
        Override generate_until to augment contexts with Wikipedia knowledge.
        This is called for generation tasks.
        """
        # Augment all requests
        augmented_requests = []
        for req in requests:
            # Request is an Instance object with args attribute
            context, gen_kwargs = req.args
            augmented_context = self._augment_context(context)
            
            # Create new request with augmented context using dataclasses.replace
            new_req = replace(req, arguments=(augmented_context, gen_kwargs))
            augmented_requests.append(new_req)
        
        # Call parent implementation with augmented requests
        return super().generate_until(augmented_requests)


def main():
    """
    Run RAG-enhanced evaluation.
    Compatible with existing dashboard.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='RAG-Enhanced Model Evaluation')
    parser.add_argument('--model', type=str, default='meta-llama/Llama-3.2-3B',
                       help='HuggingFace model name')
    parser.add_argument('--tasks', type=str, default='mmlu_global_facts',
                       help='Comma-separated list of tasks')
    parser.add_argument('--device', type=str, default='mps',
                       help='Device to use (mps, cuda, cpu)')
    parser.add_argument('--chroma_path', type=str, default='./chroma_db',
                       help='Path to ChromaDB')
    parser.add_argument('--n_retrieval', type=int, default=3,
                       help='Number of Wikipedia chunks to retrieve')
    parser.add_argument('--output_path', type=str, default='./results',
                       help='Output directory for results')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of examples (for testing)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 RAG-Enhanced Model Evaluation")
    print("=" * 60)
    
    # Initialize RAG model
    model = RAGAugmentedModel(
        pretrained=args.model,
        chroma_path=args.chroma_path,
        n_retrieval=args.n_retrieval,
        device=args.device
    )
    
    # Parse tasks
    tasks = [t.strip() for t in args.tasks.split(',')]
    
    print(f"\n📋 Running evaluation:")
    print(f"   Model: {args.model}")
    print(f"   Tasks: {tasks}")
    print(f"   Device: {args.device}")
    if args.limit:
        print(f"   Limit: {args.limit} examples")
    
    # Run evaluation using lm-eval
    results = evaluator.simple_evaluate(
        model=model,
        tasks=tasks,
        limit=args.limit,
    )
    
    # Print retrieval stats
    print(f"\n📊 Retrieval Statistics:")
    print(f"   Total retrievals performed: {model.retrieval_count}")
    
    # Save results in lm-eval format
    model_name_sanitized = args.model.replace('/', '__')
    output_dir = os.path.join(args.output_path, f"rag-{model_name_sanitized}")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().isoformat()
    output_file = os.path.join(output_dir, f"results_{timestamp}.json")
    
    # Save as JSON (using default=str to handle non-serializable objects like dtype)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✅ Evaluation complete!")
    print(f"📁 Results saved to: {output_file}")
    print(f"\n🎯 View in dashboard at: http://localhost:8080")
    
    # Print summary
    print(f"\n📈 Results Summary:")
    for task, task_results in results.get('results', {}).items():
        acc = task_results.get('acc,none', task_results.get('acc', 'N/A'))
        print(f"   {task}: {acc:.2%}" if isinstance(acc, float) else f"   {task}: {acc}")


if __name__ == '__main__':
    main()

