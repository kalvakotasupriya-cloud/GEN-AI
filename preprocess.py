import pandas as pd

# Load raw file
df = pd.read_csv("kcc1.csv")

# Keep only required columns
df = df[["QueryText", "KccAns"]]

# Rename columns (important)
df = df.rename(columns={
    "QueryText": "question",
    "KccAns": "answer"
})

# Remove empty rows
df = df.dropna()

# Remove duplicates
df = df.drop_duplicates()

# Save cleaned file
df.to_csv("clean_kcc.csv", index=False)
df.to_json("kcc_qa_pairs.json", orient="records", indent=4)

print("Cleaning completed successfully!")