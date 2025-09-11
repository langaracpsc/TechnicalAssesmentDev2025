#!/usr/bin/env python3
"""
Script to download UN General Assembly votes dataset from Hugging Face
Dataset: https://huggingface.co/datasets/sam-bha/un-general-assembly-votes-2000-2023
"""

import os
import json
import pandas as pd
from datasets import load_dataset
from datetime import datetime

def download_un_votes_dataset():
    """Download and process the UN General Assembly votes dataset"""
    
    print("Downloading UN General Assembly votes dataset...")
    
    try:
        # Load the dataset from Hugging Face
        dataset = load_dataset("sam-bha/un-general-assembly-votes-2000-2023")
        
        # Get the train split (which contains all the data)
        train_data = dataset['train']
        
        print(f"Dataset loaded successfully! Found {len(train_data)} records.")
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Convert to pandas DataFrame for easier processing
        df = pd.DataFrame(train_data)
        
        # Save as CSV
        csv_path = 'data/un_general_assembly_votes.csv'
        df.to_csv(csv_path, index=False)
        print(f"Data saved to CSV: {csv_path}")
        
        # Save as JSON for API consumption
        json_path = 'data/un_general_assembly_votes.json'
        df.to_json(json_path, orient='records', indent=2)
        print(f"Data saved to JSON: {json_path}")
        
        # Process votes for our voting application format
        processed_votes = []
        
        for idx, row in df.iterrows():
            # Extract vote data from the 'Vote' column
            if pd.notna(row['Vote']) and isinstance(row['Vote'], dict):
                vote_dict = row['Vote']
                
                # Process each country's vote
                for country, vote in vote_dict.items():
                    if vote in ['Y', 'N', 'A']:  # Yes, No, Abstain
                        processed_vote = {
                            'id': f"un_{row['id']}_{country.replace(' ', '_').replace('(', '').replace(')', '')}",
                            'candidate': vote,  # Y, N, or A
                            'voter_id': country,
                            'metadata': {
                                'resolution_id': row['id'],
                                'title': row['Title'],
                                'agenda': row['Agenda'],
                                'resolution': row['Resolution'],
                                'vote_date': row['Vote date'],
                                'vote_summary': row['Vote summary'],
                                'original_candidate': vote
                            },
                            'timestamp': row['Vote date']
                        }
                        processed_votes.append(processed_vote)
        
        # Save processed votes for our API
        processed_path = 'data/processed_votes.json'
        with open(processed_path, 'w') as f:
            json.dump(processed_votes, f, indent=2)
        print(f"Processed votes saved to: {processed_path}")
        print(f"Total processed votes: {len(processed_votes)}")
        
        # Create a sample dataset for testing (first 1000 votes)
        sample_votes = processed_votes[:1000]
        sample_path = 'data/sample_votes.json'
        with open(sample_path, 'w') as f:
            json.dump(sample_votes, f, indent=2)
        print(f"Sample dataset (1000 votes) saved to: {sample_path}")
        
        # Generate statistics
        stats = {
            'total_resolutions': len(df),
            'total_votes': len(processed_votes),
            'date_range': {
                'earliest': df['Vote date'].min(),
                'latest': df['Vote date'].max()
            },
            'vote_distribution': {
                'Yes': len([v for v in processed_votes if v['candidate'] == 'Y']),
                'No': len([v for v in processed_votes if v['candidate'] == 'N']),
                'Abstain': len([v for v in processed_votes if v['candidate'] == 'A'])
            },
            'unique_countries': len(set(v['voter_id'] for v in processed_votes)),
            'download_timestamp': datetime.now().isoformat()
        }
        
        stats_path = 'data/dataset_stats.json'
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"Dataset statistics saved to: {stats_path}")
        
        print("\nDataset download completed successfully!")
        print(f"Files created:")
        print(f"  - {csv_path}")
        print(f"  - {json_path}")
        print(f"  - {processed_path}")
        print(f"  - {sample_path}")
        print(f"  - {stats_path}")
        
        return True
        
    except Exception as e:
        print(f"Error downloading dataset: {str(e)}")
        return False

if __name__ == "__main__":
    success = download_un_votes_dataset()
    if success:
        print("\n✅ Dataset download completed successfully!")
        print("You can now use the processed_votes.json file to test the voting API.")
    else:
        print("\n❌ Dataset download failed!")
        print("Please check your internet connection and try again.")
