import os

from sentence_transformers import SentenceTransformer # type: ignore
import chromadb # type: ignore
import json
import numpy as np
from transformers import AutoTokenizer

# Load model without chunking
# model = SentenceTransformer("all-MiniLM-L6-v2")

# Load model
model_name = "all-mpnet-base-v2"
model = SentenceTransformer(model_name)
tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-mpnet-base-v2')

def chunk_text(text, max_tokens=512):
    """
    Given that data is very long, chunck document text to fit in sentence model window
    """
    words = text.split()
    chunks = []
    current_chunk = []
    for word in words:
        current_chunk.append(word)
        tokenized = tokenizer(" ".join(current_chunk), truncation=False)
        if len(tokenized['input_ids']) > max_tokens:
            current_chunk.pop()
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

# Get document embeddings (use mean of chunks)
def embed_document(text):
    chunks = chunk_text(text)
    embeddings = model.encode(chunks)
    return np.mean(embeddings, axis=0) 


# Create documents from data files
documents = []

data_files_path = ['./webscrappers/data/fridge_cleaned_data.jsonl', 
                   './webscrappers/data/dishwasher_cleaned_data.jsonl',
                   './webscrappers/data/dishwasher_repair.jsonl',
                    './webscrappers/data/fridge_repair.jsonl'
                   ]

for file_path in data_files_path:
    with open(file_path, 'r') as f:
        file_content = [json.dumps(json.loads(line)) for line in f]
        documents += file_content

# Generate embeddings from documents
# embeddings = model.encode(documents) # without chunking
embeddings = [embed_document(doc) for doc in documents]

# Connect to ChromaDB server
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
collection = client.get_or_create_collection(name="my_collection")

# Add documents
collection.add(
    documents=documents,
    embeddings=embeddings, # embeddings.tolist() without chunking
    ids=[f"doc{i}" for i in range(len(documents))],
    metadatas=[{"source": f"doc{i}"} for i in range(len(documents))]
)

print("Documents loaded into ChromaDB.")
