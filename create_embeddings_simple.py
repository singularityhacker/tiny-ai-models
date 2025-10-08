#!/usr/bin/env python3
"""
Memory-efficient Wikipedia embedding creator
"""

import os
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
from tqdm import tqdm

def main():
    print("🚀 Starting memory-efficient Wikipedia embedding creation...")
    
    # Initialize model
    print("Loading embedding model...")
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    print("✅ Model loaded!")
    
    # Initialize ChromaDB
    print("Setting up ChromaDB...")
    client = chromadb.PersistentClient(path="./chroma_db")
    
    try:
        collection = client.get_collection("simple_wikipedia")
        print("Found existing collection, clearing it...")
        client.delete_collection("simple_wikipedia")
    except:
        pass
        
    # Create collection with explicit embedding function
    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
    collection = client.create_collection(
        "simple_wikipedia",
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"}
    )
    print("✅ ChromaDB ready!")
    
    # Load dataset
    print("Loading Simple Wikipedia dataset...")
    dataset = load_dataset("wikipedia", "20220301.simple")
    train_data = dataset['train']
    
    # Process all articles
    num_articles = len(train_data)
    print(f"📊 Processing all {num_articles:,} articles...")
    
    total_chunks = 0
    processed_articles = 0
    skipped_articles = 0
    
    for i in tqdm(range(num_articles), desc="Processing articles"):
        article = train_data[i]
        title = article['title']
        text = article['text']
        
        # Simple chunking - split by paragraphs
        paragraphs = text.split('\n\n')
        chunks = []
        
        for j, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) > 100:  # Only chunks with substantial content
                chunks.append({
                    'text': paragraph.strip(),
                    'title': title,
                    'chunk_id': j
                })
        
        if chunks:
            try:
                # Create embeddings for this article's chunks
                texts = [chunk['text'] for chunk in chunks]
                embeddings = model.encode(texts, show_progress_bar=False)
                
                # Prepare data for ChromaDB
                ids = []
                documents = []
                metadatas = []
                
                for j, chunk in enumerate(chunks):
                    chunk_id = f"{title.replace(' ', '_')}_{j}"
                    ids.append(chunk_id)
                    documents.append(chunk['text'])
                    metadatas.append({
                        'title': title,
                        'chunk_id': j,
                        'article_index': i
                    })
                
                # Store in ChromaDB
                collection.add(
                    ids=ids,
                    embeddings=embeddings.tolist(),
                    documents=documents,
                    metadatas=metadatas
                )
                
                total_chunks += len(chunks)
                processed_articles += 1
                
            except Exception as e:
                print(f"\n⚠️  Error processing article '{title}': {e}")
                skipped_articles += 1
                continue
        else:
            skipped_articles += 1
    
    print(f"\n✅ Embedding creation complete!")
    print(f"📊 Statistics:")
    print(f"  Total articles: {num_articles:,}")
    print(f"  Successfully processed: {processed_articles:,}")
    print(f"  Skipped (empty/invalid): {skipped_articles:,}")
    print(f"  Total chunks created: {total_chunks:,}")
    print(f"  Average chunks per article: {total_chunks/max(processed_articles, 1):.1f}")
    
    # Test retrieval
    print(f"\n🔍 Testing retrieval...")
    results = collection.query(
        query_texts=["What is a dog?"],
        n_results=3
    )
    
    print("Sample results for 'What is a dog?':")
    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        print(f"  {i+1}. {metadata['title']} (chunk {metadata['chunk_id']})")
        print(f"     {doc[:100]}...")
    
    print(f"\n🎯 ChromaDB collection ready!")
    print(f"Location: ./chroma_db")

if __name__ == "__main__":
    main()
