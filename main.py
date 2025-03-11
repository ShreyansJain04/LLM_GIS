import PyPDF2
import camelot
import re
import io
import numpy as np
from sentence_transformers import SentenceTransformer

# 1) Extract text from PDF using PyPDF2
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {page_num+1} ---\n{page_text}\n"
    return text

# 2) Extract tables from PDF using Camelot
def extract_tables_from_pdf(pdf_path):
    tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
    dfs = []
    for t in tables:
        dfs.append(t.df)
    return dfs

# Convert a DataFrame to CSV text
def dataframe_to_text(df):
    import io
    with io.StringIO() as buffer:
        df.to_csv(buffer, index=False)
        return buffer.getvalue().strip()

def tables_to_text(dfs):
    table_texts = []
    for idx, df in enumerate(dfs):
        csv_str = dataframe_to_text(df)
        labeled_str = f"--- Table {idx+1} ---\n{csv_str}"
        table_texts.append(labeled_str)
    return table_texts

# 3) Chunk text into smaller segments
def chunk_text(text, max_chars=500):
    sentences = re.split(r'(?<=[.?!])\s+', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chars:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# 4) The main workflow
pdf_path = "/teamspace/studios/this_studio/Tricor label.pdf"  # <-- Replace with your file
pdf_text = extract_text_from_pdf(pdf_path)

table_dfs = extract_tables_from_pdf(pdf_path)
table_texts = tables_to_text(table_dfs)

# Combine plain text + table CSV text
all_text = pdf_text + "\n".join(table_texts)

# Split into chunks
chunks = chunk_text(all_text, max_chars=500)

# Embed with sentence-transformers
model = SentenceTransformer('all-MiniLM-L6-v2')
chunk_embeddings = model.encode(chunks)
chunk_embeddings = np.array(chunk_embeddings)

# Store (embedding, text_chunk) in a list
indexed_chunks = [(chunk_embeddings[i], chunks[i]) for i in range(len(chunks))]

# Retrieval function: use embedding similarity to recover chunk text
def retrieve_text_from_embedding(target_embedding, indexed_chunks, top_k=1):
    similarities = []
    for emb, txt in indexed_chunks:
        cos_sim = np.dot(emb, target_embedding) / (np.linalg.norm(emb) * np.linalg.norm(target_embedding))
        similarities.append((cos_sim, txt))
    similarities.sort(key=lambda x: x[0], reverse=True)
    return [chunk_text for _, chunk_text in similarities[:top_k]]

# Example usage: try retrieving chunk #9 from its own embedding
test_embedding = chunk_embeddings[9]
reconstructed = retrieve_text_from_embedding(test_embedding, indexed_chunks, top_k=1)

print("Original chunk:")
print(chunks[9])
print("\nReconstructed chunk:")
print(reconstructed[0],reconstructed[1])
