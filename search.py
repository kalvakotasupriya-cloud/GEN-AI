import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np

print("Loading model (offline)...")
model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)

print("Loading FAISS index...")
index = faiss.read_index("kcc_index.faiss")

print("Loading cleaned CSV...")
df = pd.read_csv("clean_kcc.csv")

while True:
    query = input("\nEnter your question (or type exit): ")

    if query.lower() == "exit":
        break

    query_embedding = model.encode([query])

    D, I = index.search(np.array(query_embedding), k=1)

    answer = df.iloc[I[0][0]]["answer"]

    print("\nAnswer:")
    print(answer)