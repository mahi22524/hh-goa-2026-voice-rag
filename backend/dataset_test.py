from datasets import load_dataset

print("Loading MSMARCO-XI...")

dataset = load_dataset(
    "ai4bharat/MSMARCO-XI",
    split="train",
    streaming=True
)

for i, row in enumerate(dataset):
    print("\n--- SAMPLE", i + 1, "---")
    print(row)

    if i == 2:
        break
