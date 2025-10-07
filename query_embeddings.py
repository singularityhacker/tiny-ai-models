#!/usr/bin/env python3
"""
Simple Wikipedia Embedding Query Tool

Query the ChromaDB vector store for relevant Wikipedia articles.
"""

import chromadb
from typing import List, Dict, Any


class WikipediaQuery:
    def __init__(self, collection_name: str = "simple_wikipedia"):
        """Initialize the query interface."""
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_collection(collection_name)
        
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant Wikipedia articles."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        for doc, metadata, distance in zip(results['documents'][0], 
                                         results['metadatas'][0], 
                                         results['distances'][0]):
            formatted_results.append({
                'title': metadata['title'],
                'chunk_id': metadata['chunk_id'],
                'text': doc,
                'relevance_score': 1 - distance,  # Convert distance to similarity
                'metadata': metadata
            })
            
        return formatted_results
        
    def print_results(self, query: str, n_results: int = 5):
        """Search and print formatted results."""
        print(f"🔍 Searching for: '{query}'")
        print("=" * 60)
        
        results = self.search(query, n_results)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']} (chunk {result['chunk_id']})")
            print(f"   Relevance: {result['relevance_score']:.3f}")
            print(f"   Text: {result['text'][:200]}...")
            
    def get_collection_stats(self):
        """Print collection statistics."""
        count = self.collection.count()
        print(f"📊 ChromaDB Collection Statistics:")
        print(f"   Total chunks: {count:,}")
        
        # Sample a few items to get article count
        sample = self.collection.get(limit=1000)
        unique_titles = set()
        for metadata in sample['metadatas']:
            unique_titles.add(metadata['title'])
            
        print(f"   Unique articles: {len(unique_titles):,}")


def main():
    """Interactive query interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Query Wikipedia embeddings")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--results", type=int, default=5, help="Number of results")
    parser.add_argument("--stats", action="store_true", help="Show collection stats")
    
    args = parser.parse_args()
    
    # Initialize query interface
    query_tool = WikipediaQuery()
    
    if args.stats:
        query_tool.get_collection_stats()
        
    if args.query:
        query_tool.print_results(args.query, args.results)
        
    if not args.query and not args.stats:
        # Interactive mode
        print("🔍 Wikipedia Embedding Query Tool")
        print("Type 'quit' to exit, 'stats' for collection statistics")
        
        while True:
            query = input("\nEnter your search query: ").strip()
            
            if query.lower() == 'quit':
                break
            elif query.lower() == 'stats':
                query_tool.get_collection_stats()
            elif query:
                query_tool.print_results(query, args.results)


if __name__ == "__main__":
    main()
