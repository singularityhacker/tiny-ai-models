#!/usr/bin/env python3
"""
Simple Wikipedia Downloader

Downloads Simple Wikipedia dataset and saves it locally for embedding creation.
This only needs to be run once - the dataset will be cached locally.
"""

import os
from datasets import load_dataset

def main():
    # Create output directory if it doesn't exist
    output_dir = "./simple_wikipedia"
    
    # Check if already downloaded
    if os.path.exists(output_dir):
        print(f"Simple Wikipedia already exists at {output_dir}")
        print("Loading existing dataset...")
        dataset = load_dataset(output_dir)
    else:
        # Download
        print("Downloading Simple Wikipedia...")
        print("This may take several minutes depending on your internet connection...")
        dataset = load_dataset("wikipedia", "20220301.simple")
        
        # Save locally
        print(f"Saving to {output_dir}...")
        dataset.save_to_disk(output_dir)
        print("✅ Download complete!")
    
    # Show statistics
    train_data = dataset['train']
    print(f"\n📊 Dataset Statistics:")
    print(f"Total articles: {len(train_data):,}")
    
    # Show sample articles
    print(f"\n📄 Sample articles:")
    for i in range(min(5, len(train_data))):
        article = train_data[i]
        title = article['title']
        text_length = len(article['text'])
        print(f"  {i+1}. {title} ({text_length:,} characters)")
    
    # Calculate total text size
    total_chars = sum(len(article['text']) for article in train_data)
    print(f"\n📏 Total text size: {total_chars:,} characters")
    print(f"📏 Total text size: {total_chars / 1_000_000:.1f} MB")
    
    print(f"\n🎯 Dataset ready for embedding creation!")
    print(f"Location: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()