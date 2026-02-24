from sentence_transformers import SentenceTransformer
import pandas as pd
import pickle
import faiss
import numpy as np

print("Loading model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

print("Loading cleaned CSV...")
df = pd.read_csv("clean_kcc.csv")

questions = df["question"].tolist()

print("Generating embeddings...")
embeddings = model.encode(questions)

with open("embeddings.pkl", "wb") as f:
    pickle.dump(embeddings, f)

print("Creating FAISS index...")
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))

faiss.write_index(index, "kcc_index.faiss")

print("Embeddings and FAISS index created successfully!")