import faiss
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

print("Loading model...")
model = SentenceTransformer(
    "all-MiniLM-L6-v2",
    local_files_only=False   # Allow download if needed
)

print("Loading cleaned CSV...")
df = pd.read_csv("clean_kcc.csv")

print("Creating embeddings...")
embeddings = model.encode(df["question"].tolist())

dimension = embeddings.shape[1]

print("Building FAISS index...")
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

faiss.write_index(index, "kcc_index.faiss")

print("✅ FAISS index created successfully!")