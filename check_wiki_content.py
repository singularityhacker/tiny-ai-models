#!/usr/bin/env python3
"""
Check what's actually in the Simple Wikipedia dataset
"""

from datasets import load_dataset

def main():
    print("Loading Simple Wikipedia dataset...")
    dataset = load_dataset("./simple_wikipedia")
    
    train_data = dataset['train']
    print(f"Train data length: {len(train_data)}")
    
    # Try to access the actual data
    print("Checking the actual data structure...")
    
    # Get the first item and examine it thoroughly
    first_item = train_data[0]
    print(f"First item type: {type(first_item)}")
    print(f"First item keys: {list(first_item.keys())}")
    
    # Check if there are actual articles in the data attribute
    print("\nChecking train_data.data...")
    try:
        data_table = train_data.data
        print(f"Data table type: {type(data_table)}")
        print(f"Data table shape: {data_table.shape}")
        print(f"Data table column names: {data_table.column_names}")
        
        # Try to get actual content
        if data_table.num_rows > 0:
            print(f"\nFirst row from data table:")
            first_row = data_table.slice(0, 1).to_pydict()
            for key, value in first_row.items():
                if isinstance(value[0], str) and len(value[0]) > 100:
                    print(f"  {key}: {value[0][:100]}...")
                else:
                    print(f"  {key}: {value[0]}")
                    
    except Exception as e:
        print(f"Error accessing data: {e}")
    
    # Try alternative loading method
    print("\nTrying to reload from HuggingFace directly...")
    try:
        fresh_dataset = load_dataset("wikipedia", "20220301.simple")
        print(f"Fresh dataset train length: {len(fresh_dataset['train'])}")
        if len(fresh_dataset['train']) > 0:
            sample = fresh_dataset['train'][0]
            print(f"Sample keys: {list(sample.keys())}")
            print(f"Sample title: {sample.get('title', 'NO TITLE')}")
            print(f"Sample text length: {len(sample.get('text', ''))}")
    except Exception as e:
        print(f"Error loading fresh dataset: {e}")

if __name__ == "__main__":
    main()
