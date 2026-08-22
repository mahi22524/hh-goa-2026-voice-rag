import sys
import os
import argparse
from huggingface_hub import HfApi
from datasets import get_dataset_config_names, get_dataset_split_names, load_dataset

def main():
    # Reconfigure stdout/stderr to support UTF-8 characters (e.g. Indic scripts) on Windows
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Resource-conscious Hugging Face dataset inspector.")
    parser.add_argument(
        "--split",
        type=str,
        default="train",
        choices=["train", "validation"],
        help="The dataset split to inspect (defaults to 'train')."
    )
    args = parser.parse_args()
    
    dataset_id = "ai4bharat/MSMARCO-XI"
    print("==================================================", flush=True)
    print(f"Inspecting Dataset: {dataset_id}", flush=True)
    print("==================================================\n", flush=True)
    
    # 1. Available Configurations
    print("1. Querying Available Configurations...", flush=True)
    try:
        configs = get_dataset_config_names(dataset_id)
        print("Discovered Configurations:", flush=True)
        for config in configs:
            print(f"  - {config}", flush=True)
    except Exception as e:
        print(f"Error querying configurations: {e}", flush=True)
        configs = []
        
    if not configs:
        configs = ["default"]
        print("Using fallback configuration: 'default'", flush=True)
        
    chosen_config = configs[0]
    print(f"Selected configuration for metadata lookup: '{chosen_config}'\n", flush=True)
    
    # 2. Available Splits
    print("2. Querying Available Splits...", flush=True)
    try:
        splits = get_dataset_split_names(dataset_id, config_name=chosen_config)
        print("Discovered Splits:", flush=True)
        for split in splits:
            print(f"  - {split}", flush=True)
    except Exception as e:
        print(f"Error querying splits: {e}", flush=True)
        splits = []
        
    if not splits:
        splits = ["train", "validation"]
        print("Using fallback splits: ['train', 'validation']", flush=True)
        
    # Set chosen split based on command line args or availability
    chosen_split = args.split if args.split in splits else splits[0]
    print(f"Selected split for inspection: '{chosen_split}'\n", flush=True)
    
    # 3. Dynamic Repository File Discovery (to locate individual parquet files and sizes)
    print("3. Querying Repository Files to identify individual language chunks...", flush=True)
    try:
        api = HfApi()
        repo_files = list(api.list_repo_tree(repo_id=dataset_id, repo_type="dataset", recursive=True))
        parquet_files = [f for f in repo_files if f.path.endswith('.parquet')]
    except Exception as e:
        print(f"Error listing repo files from HF Hub: {e}", flush=True)
        parquet_files = []
        
    train_parquets = []
    val_parquets = []
    
    for f in parquet_files:
        if f.path.startswith("train/"):
            train_parquets.append(f)
        elif f.path.startswith("validation/"):
            val_parquets.append(f)
            
    print(f"Discovered {len(parquet_files)} parquet files in repository:", flush=True)
    print(f"  - {len(train_parquets)} files in 'train' directory", flush=True)
    print(f"  - {len(val_parquets)} files in 'validation' directory\n", flush=True)
    
    # Identify the smallest file in the selected split to optimize bandwidth
    selected_files_pool = train_parquets if chosen_split == "train" else val_parquets
    if not selected_files_pool:
        selected_files_pool = parquet_files
        
    if selected_files_pool:
        smallest_file_obj = min(selected_files_pool, key=lambda f: f.size)
        target_file_path = smallest_file_obj.path
        target_file_size_mb = smallest_file_obj.size / (1024 * 1024)
        print(f"Resource-Safety Optimization:", flush=True)
        print(f"  To avoid downloading the entire 50GB dataset, the script will load", flush=True)
        print(f"  only the smallest parquet file in the '{chosen_split}' split.", flush=True)
        print(f"  Target File: '{target_file_path}' ({target_file_size_mb:.2f} MB)\n", flush=True)
    else:
        target_file_path = None
        print("No specific parquet files found. Loading the default streaming stream...\n", flush=True)
        
    # 4. Load dataset with streaming=True
    print(f"4. Loading dataset in streaming mode...", flush=True)
    try:
        if target_file_path:
            # Map target_file_path to a dictionary matching the chosen_split to ensure the correct split is generated
            dataset = load_dataset(
                dataset_id,
                data_files={chosen_split: target_file_path},
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
        print(f"Error initializing streaming dataset: {e}", flush=True)
        sys.exit(1)
        
    # 5. Schema / Field Names
    print("\n5. Extracting Dataset Schema / Field Names...", flush=True)
    try:
        features = dataset.features
        for field, f_type in features.items():
            print(f"  - {field}: {f_type}", flush=True)
    except Exception as e:
        print(f"Could not retrieve features schema directly from object: {e}", flush=True)
        
    # 6. Fetch a single sample record
    print("\n6. Retrieving one sample record from the stream...", flush=True)
    sample_record = None
    try:
        for record in dataset:
            sample_record = record
            break
    except Exception as e:
        print(f"Error fetching sample record: {e}", flush=True)
        sys.exit(1)
        
    if sample_record is None:
        print("No records found in dataset stream.", flush=True)
        sys.exit(0)
        
    print("\n==================================================", flush=True)
    print("SAMPLE RECORD VALUES (Truncated for readability)", flush=True)
    print("==================================================", flush=True)
    
    def truncate_value(val, max_len=150):
        if isinstance(val, str):
            if len(val) > max_len:
                return val[:max_len] + f"... [TRUNCATED - Total Length: {len(val)} characters]"
            return val
        elif isinstance(val, list):
            # Truncate list elements and length
            truncated_list = [truncate_value(item, max_len=50) for item in val[:3]]
            if len(val) > 3:
                return truncated_list + [f"... [TRUNCATED - Total Items: {len(val)}]"]
            return truncated_list
        elif isinstance(val, dict):
            # Truncate dict keys and value elements
            truncated_dict = {k: truncate_value(v, max_len=50) for k, v in list(val.items())[:3]}
            if len(val) > 3:
                truncated_dict["..."] = f"[TRUNCATED - Total Keys: {len(val)}]"
            return truncated_dict
        return val

    for field, value in sample_record.items():
        truncated = truncate_value(value)
        print(f"Field Name : {field}", flush=True)
        print(f"Data Type  : {type(value).__name__}", flush=True)
        print(f"Sample Value: {truncated}", flush=True)
        print("-" * 50, flush=True)

if __name__ == "__main__":
    main()
