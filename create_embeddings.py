#!/usr/bin/env python3
"""
Simple Wikipedia Embedding Creator

Creates embeddings for Simple Wikipedia articles and stores them in ChromaDB.
Uses sentence-transformers/all-mpnet-base-v2 for high-quality embeddings.
"""

import os
import json
import re
from typing import List, Dict, Any
from datetime import datetime

import chromadb
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
from tqdm import tqdm


class WikipediaEmbeddingCreator:
    def __init__(self, 
                 embedding_model: str = "sentence-transformers/all-mpnet-base-v2",
                 chunk_size: int = 512,
                 overlap: int = 50,
                 batch_size: int = 100):
        """
        Initialize the embedding creator.
        
        Args:
            embedding_model: Name of the sentence transformer model
            chunk_size: Maximum tokens per chunk
            overlap: Number of tokens to overlap between chunks
            batch_size: Number of articles to process at once
        """
        self.embedding_model_name = embedding_model
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.batch_size = batch_size
        
        # Initialize components
        self.model = None
        self.chroma_client = None
        self.collection = None
        
    def setup_model(self):
        """Load the sentence transformer model."""
        print(f"Loading embedding model: {self.embedding_model_name}")
        print("This may take a moment on first run...")
        self.model = SentenceTransformer(self.embedding_model_name)
        print("✅ Model loaded successfully!")
        
    def setup_chromadb(self, collection_name: str = "simple_wikipedia"):
        """Initialize ChromaDB client and collection."""
        print("Setting up ChromaDB...")
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        # Create or get collection
        try:
            self.collection = self.chroma_client.get_collection(collection_name)
            print(f"Found existing collection: {collection_name}")
        except:
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"description": "Simple Wikipedia embeddings"}
            )
            print(f"Created new collection: {collection_name}")
            
        print("✅ ChromaDB ready!")
        
    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove Wikipedia markup (basic cleanup)
        text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)  # Remove [[]] markup
        text = re.sub(r'\[([^\]]+)\]', r'\1', text)      # Remove [] links
        text = re.sub(r'\{\{[^\}]+\}\}', '', text)       # Remove {{}} templates
        return text
        
    def split_text_into_chunks(self, text: str, title: str) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks."""
        # Simple token-based splitting (approximate)
        words = text.split()
        chunks = []
        
        start = 0
        chunk_id = 0
        
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            
            if chunk_text.strip():  # Only add non-empty chunks
                chunks.append({
                    'text': chunk_text,
                    'title': title,
                    'chunk_id': chunk_id,
                    'start_word': start,
                    'end_word': end,
                    'total_words': len(words)
                })
                chunk_id += 1
                
            start = end - self.overlap  # Overlap for context
            
        return chunks
        
    def process_article(self, article: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a single article into chunks."""
        # Simple Wikipedia uses 'title' and 'text' keys
        title = article.get('title', 'Unknown Title')
        text = article.get('text', '')
        
        # Clean and process text
        text = self.clean_text(text)
        
        # Skip empty articles
        if not text.strip():
            return []
        
        # Split into chunks
        chunks = self.split_text_into_chunks(text, title)
        
        return chunks
        
    def process_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of articles."""
        all_chunks = []
        
        for article in articles:
            chunks = self.process_article(article)
            all_chunks.extend(chunks)
            
        return all_chunks
        
    def create_embeddings_batch(self, chunks: List[Dict[str, Any]]) -> List[List[float]]:
        """Create embeddings for a batch of text chunks."""
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()
        
    def store_in_chromadb(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Store chunks and embeddings in ChromaDB."""
        ids = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            # Create unique ID
            chunk_id = f"{chunk['title'].replace(' ', '_')}_{chunk['chunk_id']}"
            ids.append(chunk_id)
            documents.append(chunk['text'])
            metadatas.append({
                'title': chunk['title'],
                'chunk_id': chunk['chunk_id'],
                'start_word': chunk['start_word'],
                'end_word': chunk['end_word'],
                'total_words': chunk['total_words'],
                'created_at': datetime.now().isoformat()
            })
            
        # Add to ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
    def create_embeddings(self, dataset_path: str = "./simple_wikipedia"):
        """Main method to create embeddings from Simple Wikipedia."""
        print("🚀 Starting Wikipedia embedding creation...")
        
        # Setup
        self.setup_model()
        self.setup_chromadb()
        
        # Load dataset
        print("Loading Simple Wikipedia dataset...")
        
        # Load directly from HuggingFace to ensure we get the right format
        if dataset_path == "./simple_wikipedia":
            print("Loading from HuggingFace directly...")
            dataset = load_dataset("wikipedia", "20220301.simple")
        else:
            dataset = load_dataset(dataset_path)
            
        train_dataset = dataset['train']
        total_articles = len(train_dataset)
        
        # Debug: Check first article structure
        if total_articles > 0:
            first_article = train_dataset[0]
            print(f"📋 First article keys: {list(first_article.keys())}")
            print(f"📋 Sample title: {first_article.get('title', 'NO TITLE')}")
            print(f"📋 Sample text length: {len(first_article.get('text', ''))}")
        
        print(f"📊 Processing {total_articles:,} articles...")
        
        # Limit articles for testing (remove this line for full processing)
        if total_articles > 1000:
            print("🔧 Limiting to first 1000 articles for testing...")
            total_articles = 1000
        
        # Process in batches
        total_chunks = 0
        total_embeddings = 0
        
        for batch_start in tqdm(range(0, total_articles, self.batch_size), 
                               desc="Processing articles"):
            batch_end = min(batch_start + self.batch_size, total_articles)
            batch_articles = [train_dataset[i] for i in range(batch_start, batch_end)]
            
            # Process batch
            chunks = self.process_batch(batch_articles)
            if not chunks:
                continue
                
            # Create embeddings
            embeddings = self.create_embeddings_batch(chunks)
            
            # Store in ChromaDB
            self.store_in_chromadb(chunks, embeddings)
            
            total_chunks += len(chunks)
            total_embeddings += len(embeddings)
            
            # Progress update
            if batch_start % (self.batch_size * 10) == 0:
                print(f"  Processed {batch_end:,}/{total_articles:,} articles")
                print(f"  Created {total_chunks:,} chunks, {total_embeddings:,} embeddings")
                
        print(f"\n✅ Embedding creation complete!")
        print(f"📊 Final Statistics:")
        print(f"  Articles processed: {total_articles:,}")
        print(f"  Total chunks created: {total_chunks:,}")
        print(f"  Total embeddings: {total_embeddings:,}")
        print(f"  Average chunks per article: {total_chunks/total_articles:.1f}")
        
        # Test retrieval
        print(f"\n🔍 Testing retrieval...")
        test_results = self.collection.query(
            query_texts=["What is a dog?"],
            n_results=3
        )
        
        print("Sample results for 'What is a dog?':")
        for i, (doc, metadata) in enumerate(zip(test_results['documents'][0], 
                                               test_results['metadatas'][0])):
            print(f"  {i+1}. {metadata['title']} (chunk {metadata['chunk_id']})")
            print(f"     {doc[:100]}...")
            
        print(f"\n🎯 ChromaDB collection ready for use!")
        print(f"Location: ./chroma_db")


def main():
    """Main function to run embedding creation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create Wikipedia embeddings")
    parser.add_argument("--model", 
                       default="sentence-transformers/all-mpnet-base-v2",
                       help="Embedding model to use")
    parser.add_argument("--chunk-size", type=int, default=512,
                       help="Maximum tokens per chunk")
    parser.add_argument("--batch-size", type=int, default=100,
                       help="Number of articles to process at once")
    parser.add_argument("--dataset-path", default="./simple_wikipedia",
                       help="Path to Simple Wikipedia dataset")
    
    args = parser.parse_args()
    
    # Create embedding creator
    creator = WikipediaEmbeddingCreator(
        embedding_model=args.model,
        chunk_size=args.chunk_size,
        batch_size=args.batch_size
    )
    
    # Run embedding creation
    creator.create_embeddings(args.dataset_path)


if __name__ == "__main__":
    main()
