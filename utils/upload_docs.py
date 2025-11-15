import os
import glob
import pinecone
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv
load_dotenv()
import os

# ------------------------
# CONFIG
# ------------------------
INDEX_NAME = os.getenv("PINECONE_INDEX") or "insurance-docs-index"
DOC_FOLDER = "E:\FairQuote\utils\insurance_docs"  # your folder with .txt docs
EMBEDDING_MODEL_NAME = "Qwen/Qwen3-Embedding-8B"
CHUNK_SIZE = 250  # approximate tokens per chunk

# ------------------------
# Initialize Pinecone
# ------------------------
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENV")
)

if INDEX_NAME not in pinecone.list_indexes():
    pinecone.create_index(INDEX_NAME, dimension=4096)  # Qwen3-Embedding-8B has 4096 dim

index = pinecone.Index(INDEX_NAME)

# ------------------------
# Load embedding model
# ------------------------
print("Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL_NAME)
print("Model loaded.")

# ------------------------
# Helper: chunk text by words
# ------------------------
def chunk_text(text, chunk_size=CHUNK_SIZE):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

# ------------------------
# Ingest documents
# ------------------------
for filepath in glob.glob(f"{DOC_FOLDER}/*.txt"):
    filename = os.path.basename(filepath)
    title = filename.replace(".txt", "")

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)
    vectors = []

    print(f"Uploading {len(chunks)} chunks for {filename}...")

    for i, chunk in enumerate(chunks):
        # Generate embedding
        emb = model.encode(chunk)
        emb = emb.tolist()  # convert to list for Pinecone

        # Metadata
        metadata = {
            "source_file": filename,
            "title": title,
            "chunk_index": i,
            "text": chunk
        }

        # Add to batch
        vectors.append((f"{title}-{i}", emb, metadata))

    # Upsert batch to Pinecone
    index.upsert(vectors)
    print(f"✅ Uploaded {len(chunks)} chunks for {filename}")

print("🎉 All documents ingested!")
