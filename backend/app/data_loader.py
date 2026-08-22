import sys
from huggingface_hub import HfApi
from datasets import load_dataset, get_dataset_config_names, get_dataset_split_names

def load_dev_sample(sample_size=100, split="train"):
    """
    Streams a small controlled sample of records from the official ai4bharat/MSMARCO-XI dataset.
    Uses HfApi to select the smallest parquet file in the chosen split to optimize bandwidth.
    """
    dataset_id = "ai4bharat/MSMARCO-XI"
    print(f"Loading development sample (size: {sample_size}, split: '{split}') from {dataset_id}...", flush=True)
    
    # 1. Fetch available configurations and splits
    try:
        configs = get_dataset_config_names(dataset_id)
        chosen_config = configs[0] if configs else "default"
    except Exception:
        chosen_config = "default"
        
    try:
        splits = get_dataset_split_names(dataset_id, config_name=chosen_config)
    except Exception:
        splits = [split]
        
    chosen_split = split if split in splits else splits[0]
    
    # 2. Dynamic Repo Discovery to locate the smallest file in the split
    target_file = None
    try:
        api = HfApi()
        repo_files = list(api.list_repo_tree(repo_id=dataset_id, repo_type="dataset", recursive=True))
        parquet_files = [f for f in repo_files if f.path.endswith('.parquet')]
        
        prefix = f"{chosen_split}/"
        split_files = [f for f in parquet_files if f.path.startswith(prefix)]
        
        if split_files:
            smallest_file_obj = min(split_files, key=lambda f: f.size)
            target_file = smallest_file_obj.path
            print(f"Resource-Safety: loading single file '{target_file}' ({smallest_file_obj.size / (1024*1024):.2f} MB)", flush=True)
    except Exception as e:
        print(f"Error querying repo tree (will fallback to default config): {e}", flush=True)
        
    # 3. Load dataset in streaming mode
    try:
        if target_file:
            dataset = load_dataset(
                dataset_id,
                data_files={chosen_split: target_file},
                split=chosen_split,
                streaming=True
            )
        else:
            dataset = load_dataset(
                dataset_id,
                name=chosen_config,
                split=chosen_split,
                streaming=True
            )
    except Exception as e:
        print(f"Critical error loading dataset stream: {e}", flush=True)
        raise e
        
    # 4. Fetch sample_size records
    records = []
    try:
        for record in dataset:
            records.append(record)
            if len(records) >= sample_size:
                break
    except Exception as e:
        print(f"Error streaming records: {e}", flush=True)
        
    print(f"Loaded {len(records)} records from dataset stream.", flush=True)
    return records


def extract_passages(records):
    """
    Extracts individual passages from raw dataset records, preserving metadata.
    Returns a list of passage dicts:
    [
        {
            'text': passage_text,
            'metadata': { ... }
        },
        ...
    ]
    """
    passages_list = []
    
    # Metadata fields to copy if they exist in the source record
    metadata_fields = [
        "query_id", "query", "Eng_Query", "Answer", "Eng_Answer",
        "source_lang", "target_lang"
    ]
    
    for record in records:
        passages_data = record.get("passages", {})
        if not passages_data:
            continue
            
        english_passages = passages_data.get("English_passages", [])
        translated_passages = passages_data.get("Translated_passages", [])
        is_selected_list = passages_data.get("is_selected", [])
        
        # Determine number of passages in this record
        num_passages = max(len(english_passages), len(translated_passages))
        
        for i in range(num_passages):
            # Extract common metadata
            base_metadata = {}
            for field in metadata_fields:
                if field in record:
                    base_metadata[field] = record[field]
                    
            base_metadata["passage_index"] = i
            
            # Extract is_selected value for this index
            is_selected = 0
            if i < len(is_selected_list):
                try:
                    is_selected = int(is_selected_list[i])
                except (ValueError, TypeError):
                    is_selected = 0
            base_metadata["is_selected"] = is_selected
            
            # 1. Process English passage if available
            if i < len(english_passages) and english_passages[i]:
                meta_en = base_metadata.copy()
                meta_en["language"] = "en"
                passages_list.append({
                    "text": english_passages[i],
                    "metadata": meta_en
                })
                
            # 2. Process Translated passage if available
            if i < len(translated_passages) and translated_passages[i]:
                meta_trans = base_metadata.copy()
                # Use target_lang from record if available, else default to 'translated'
                meta_trans["language"] = record.get("target_lang", "translated")
                passages_list.append({
                    "text": translated_passages[i],
                    "metadata": meta_trans
                })
                
    return passages_list
