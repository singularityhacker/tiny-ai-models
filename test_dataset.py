#!/usr/bin/env python3
"""
Test script to understand the Simple Wikipedia dataset structure
"""

from datasets import load_dataset

def main():
    print("Loading Simple Wikipedia dataset...")
    dataset = load_dataset("./simple_wikipedia")
    
    print(f"Dataset type: {type(dataset)}")
    print(f"Dataset keys: {list(dataset.keys())}")
    
    train_data = dataset['train']
    print(f"Train data type: {type(train_data)}")
    print(f"Train data length: {len(train_data)}")
    
    # Try to access the first item properly
    print("\nTrying different access methods:")
    
    # Method 1: Direct indexing
    try:
        first_item = train_data[0]
        print(f"Method 1 - Direct indexing: {type(first_item)}")
        print(f"Keys: {list(first_item.keys()) if hasattr(first_item, 'keys') else 'No keys method'}")
    except Exception as e:
        print(f"Method 1 failed: {e}")
    
    # Method 2: Iterate
    try:
        print("Method 2 - First few items via iteration:")
        for i, item in enumerate(train_data):
            if i >= 3:  # Only show first 3
                break
            print(f"  Item {i}: {type(item)} - {list(item.keys()) if hasattr(item, 'keys') else str(item)[:100]}")
    except Exception as e:
        print(f"Method 2 failed: {e}")
    
    # Method 3: Check if it's a different structure
    print(f"\nTrain data attributes: {dir(train_data)}")
    
    # Try to get actual data
    if hasattr(train_data, 'data'):
        print(f"Has data attribute: {type(train_data.data)}")
    if hasattr(train_data, '_data'):
        print(f"Has _data attribute: {type(train_data._data)}")

if __name__ == "__main__":
    main()
