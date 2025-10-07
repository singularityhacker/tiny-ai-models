#!/usr/bin/env python3
"""
Debug script to check Simple Wikipedia dataset structure
"""

from datasets import load_dataset

def main():
    # Load dataset
    print("Loading Simple Wikipedia dataset...")
    dataset = load_dataset("./simple_wikipedia")
    
    # Check structure
    print(f"Dataset keys: {list(dataset.keys())}")
    print(f"Train split size: {len(dataset['train'])}")
    
    # Check first article structure
    first_article = dataset['train'][0]
    print(f"\nFirst article keys: {list(first_article.keys())}")
    print(f"First article content:")
    for key, value in first_article.items():
        if isinstance(value, str) and len(value) > 100:
            print(f"  {key}: {value[:100]}...")
        else:
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
