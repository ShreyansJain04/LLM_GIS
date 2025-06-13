"""Advanced RAG System with Hybrid Search and Reranking."""
import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import hashlib

import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
import torch

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None

try:
    import faiss
except ImportError:
    faiss = None

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None


@dataclass
class Document:
    """Enhanced document representation with metadata."""
    id: str
    text: str
    source: str
    page: Optional[int] = None
    chunk_index: int = 0
    metadata: Dict[str, Any] = None
    embedding: Optional[np.ndarray] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        # Generate unique ID if not provided
        if not self.id:
            content = f"{self.source}_{self.page}_{self.chunk_index}_{self.text[:50]}"
            self.id = hashlib.md5(content.encode()).hexdigest()
    
    def get_citation(self) -> str:
        """Generate citation for this document."""
        source_name = Path(self.source).stem
        if self.page is not None:
            return f"[{source_name}, p. {self.page}]"
        return f"[{source_name}]"


class HybridRetriever:
    """Advanced retriever with hybrid search capabilities."""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        # Initialize models
        self.embedder = SentenceTransformer(embedding_model)
        self.reranker = CrossEncoder(rerank_model) if rerank_model else None
        
        # Storage
        self.documents: List[Document] = []
        self.bm25 = None
        self.index = None  # FAISS or ChromaDB
        self.use_gpu = torch.cuda.is_available()
        
        # Paths
        self.cache_dir = Path("rag_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
    def add_documents(self, documents: List[Document], batch_size: int = 32):
        """Add documents to the retriever with batched embedding generation."""
        print(f"Adding {len(documents)} documents to RAG system...")
        
        # Generate embeddings in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            texts = [doc.text for doc in batch]
            
            # Generate embeddings
            embeddings = self.embedder.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False,
                device='cuda' if self.use_gpu else 'cpu'
            )
            
            # Assign embeddings to documents
            for doc, embedding in zip(batch, embeddings):
                doc.embedding = embedding
                self.documents.append(doc)
        
        # Build indices
        self._build_sparse_index()
        self._build_dense_index()
        
        # Cache the processed documents
        self._save_cache()
        
    def _build_sparse_index(self):
        """Build BM25 index for sparse retrieval."""
        if BM25Okapi is None:
            print("Warning: rank-bm25 not installed. Skipping sparse index.")
            return
            
        # Tokenize documents for BM25
        tokenized_docs = [doc.text.lower().split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized_docs)
        
    def _build_dense_index(self):
        """Build FAISS/ChromaDB index for dense retrieval."""
        if not self.documents:
            return
            
        embeddings = np.array([doc.embedding for doc in self.documents])
        
        if faiss is not None:
            # Use FAISS for efficient similarity search
            dimension = embeddings.shape[1]
            
            # Choose index type based on dataset size
            if len(self.documents) < 10000:
                # For small datasets, use exact search
                self.index = faiss.IndexFlatIP(dimension)
            else:
                # For larger datasets, use approximate search
                self.index = faiss.IndexIVFFlat(
                    faiss.IndexFlatIP(dimension),
                    dimension,
                    min(len(self.documents) // 10, 100)
                )
                self.index.train(embeddings)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings)
            
        elif chromadb is not None:
            # Use ChromaDB as alternative
            self._init_chromadb(embeddings)
        else:
            print("Warning: Neither FAISS nor ChromaDB installed. Using numpy for similarity search.")
            
    def _init_chromadb(self, embeddings):
        """Initialize ChromaDB collection."""
        client = chromadb.Client(Settings(persist_directory=str(self.cache_dir)))
        
        # Create or get collection
        try:
            self.collection = client.create_collection("documents")
        except:
            client.delete_collection("documents")
            self.collection = client.create_collection("documents")
        
        # Add documents
        self.collection.add(
            embeddings=[emb.tolist() for emb in embeddings],
            documents=[doc.text for doc in self.documents],
            metadatas=[{"source": doc.source, "page": doc.page} for doc in self.documents],
            ids=[doc.id for doc in self.documents]
        )
    
    def search(
        self,
        query: str,
        k: int = 5,
        use_reranking: bool = True,
        filters: Optional[Dict[str, Any]] = None,
        alpha: float = 0.5  # Weight for hybrid search (0=sparse only, 1=dense only)
    ) -> List[Tuple[Document, float]]:
        """Perform hybrid search with optional reranking."""
        
        # Get candidates from both sparse and dense search
        sparse_results = self._sparse_search(query, k * 3) if alpha < 1 else []
        dense_results = self._dense_search(query, k * 3) if alpha > 0 else []
        
        # Combine results with weighted scores
        combined_scores = {}
        
        # Add sparse results
        for doc, score in sparse_results:
            combined_scores[doc.id] = (1 - alpha) * score
        
        # Add dense results
        for doc, score in dense_results:
            if doc.id in combined_scores:
                combined_scores[doc.id] += alpha * score
            else:
                combined_scores[doc.id] = alpha * score
        
        # Get top candidates
        candidates = []
        for doc_id, score in combined_scores.items():
            doc = next(d for d in self.documents if d.id == doc_id)
            candidates.append((doc, score))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        candidates = candidates[:k * 2]  # Keep more for reranking
        
        # Apply filters if provided
        if filters:
            candidates = self._apply_filters(candidates, filters)
        
        # Rerank if enabled
        if use_reranking and self.reranker and candidates:
            candidates = self._rerank(query, candidates, k)
        else:
            candidates = candidates[:k]
        
        return candidates
    
    def _sparse_search(self, query: str, k: int) -> List[Tuple[Document, float]]:
        """BM25 sparse search."""
        if self.bm25 is None:
            return []
        
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top k documents
        top_indices = np.argsort(scores)[-k:][::-1]
        results = []
        
        for idx in top_indices:
            if scores[idx] > 0:
                results.append((self.documents[idx], float(scores[idx])))
        
        return results
    
    def _dense_search(self, query: str, k: int) -> List[Tuple[Document, float]]:
        """Dense embedding search."""
        # Generate query embedding
        query_embedding = self.embedder.encode(
            query,
            convert_to_numpy=True,
            device='cuda' if self.use_gpu else 'cpu'
        )
        
        if faiss is not None and self.index is not None:
            # FAISS search
            query_embedding = query_embedding.reshape(1, -1)
            faiss.normalize_L2(query_embedding)
            scores, indices = self.index.search(query_embedding, k)
            
            results = []
            for idx, score in zip(indices[0], scores[0]):
                if idx >= 0:  # FAISS returns -1 for missing results
                    results.append((self.documents[idx], float(score)))
            return results
            
        elif chromadb is not None and hasattr(self, 'collection'):
            # ChromaDB search
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=k
            )
            
            doc_results = []
            for i, doc_id in enumerate(results['ids'][0]):
                doc = next(d for d in self.documents if d.id == doc_id)
                score = 1 - results['distances'][0][i]  # Convert distance to similarity
                doc_results.append((doc, score))
            return doc_results
            
        else:
            # Fallback to numpy similarity
            embeddings = np.array([doc.embedding for doc in self.documents])
            similarities = np.dot(embeddings, query_embedding)
            top_indices = np.argsort(similarities)[-k:][::-1]
            
            results = []
            for idx in top_indices:
                results.append((self.documents[idx], float(similarities[idx])))
            return results
    
    def _rerank(self, query: str, candidates: List[Tuple[Document, float]], k: int) -> List[Tuple[Document, float]]:
        """Rerank candidates using cross-encoder."""
        if not candidates:
            return candidates
        
        # Prepare query-document pairs
        pairs = [[query, doc.text] for doc, _ in candidates]
        
        # Get reranking scores
        rerank_scores = self.reranker.predict(pairs)
        
        # Combine with retrieval scores (weighted average)
        reranked = []
        for i, (doc, retrieval_score) in enumerate(candidates):
            # Normalize scores to [0, 1]
            normalized_retrieval = (retrieval_score + 1) / 2  # Assuming [-1, 1] range
            normalized_rerank = (rerank_scores[i] + 1) / 2
            
            # Weighted combination (favor reranking score)
            combined_score = 0.3 * normalized_retrieval + 0.7 * normalized_rerank
            reranked.append((doc, combined_score))
        
        # Sort by combined score
        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked[:k]
    
    def _apply_filters(self, candidates: List[Tuple[Document, float]], filters: Dict[str, Any]) -> List[Tuple[Document, float]]:
        """Apply metadata filters to candidates."""
        filtered = []
        
        for doc, score in candidates:
            include = True
            
            # Check each filter
            for key, value in filters.items():
                if key == "source" and doc.source != value:
                    include = False
                    break
                elif key == "min_score" and score < value:
                    include = False
                    break
                elif key in doc.metadata and doc.metadata[key] != value:
                    include = False
                    break
            
            if include:
                filtered.append((doc, score))
        
        return filtered
    
    def _save_cache(self):
        """Save processed documents and indices to cache."""
        cache_file = self.cache_dir / "rag_cache.pkl"
        
        cache_data = {
            'documents': self.documents,
            'bm25': self.bm25,
            'timestamp': datetime.now().isoformat()
        }
        
        with cache_file.open('wb') as f:
            pickle.dump(cache_data, f)
        
        # Save FAISS index separately
        if faiss is not None and self.index is not None:
            faiss.write_index(self.index, str(self.cache_dir / "faiss.index"))
    
    def load_cache(self) -> bool:
        """Load cached documents and indices."""
        cache_file = self.cache_dir / "rag_cache.pkl"
        
        if not cache_file.exists():
            return False
        
        try:
            with cache_file.open('rb') as f:
                cache_data = pickle.load(f)
            
            self.documents = cache_data['documents']
            self.bm25 = cache_data['bm25']
            
            # Load FAISS index
            faiss_index_file = self.cache_dir / "faiss.index"
            if faiss is not None and faiss_index_file.exists():
                self.index = faiss.read_index(str(faiss_index_file))
            
            print(f"Loaded RAG cache from {cache_data['timestamp']}")
            return True
            
        except Exception as e:
            print(f"Error loading cache: {e}")
            return False


class AdvancedRAGSystem:
    """Main RAG system with document processing and retrieval."""
    
    def __init__(
        self,
        docs_path: Path = Path("docs"),
        embedding_model: str = "all-MiniLM-L6-v2",
        rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        chunk_size: int = 512,
        chunk_overlap: int = 128
    ):
        self.docs_path = docs_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.retriever = HybridRetriever(embedding_model, rerank_model)
        
        # Try to load from cache first
        if not self.retriever.load_cache():
            self._process_documents()
    
    def _process_documents(self):
        """Process all documents in the docs directory."""
        documents = []
        
        # Process text files
        for txt_file in self.docs_path.glob("*.txt"):
            docs = self._process_text_file(txt_file)
            documents.extend(docs)
        
        # Process PDF files
        try:
            import pdfplumber
            for pdf_file in self.docs_path.glob("*.pdf"):
                docs = self._process_pdf_file(pdf_file)
                documents.extend(docs)
        except ImportError:
            print("pdfplumber not installed, skipping PDF files")
        
        # Add to retriever
        if documents:
            self.retriever.add_documents(documents)
        else:
            print("No documents found to process")
    
    def _process_text_file(self, file_path: Path) -> List[Document]:
        """Process a text file into documents."""
        content = file_path.read_text(encoding='utf-8')
        chunks = self._chunk_text(content)
        
        documents = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                doc = Document(
                    id="",
                    text=chunk,
                    source=str(file_path),
                    chunk_index=i,
                    metadata={'file_type': 'txt', 'chunk_size': len(chunk)}
                )
                documents.append(doc)
        
        return documents
    
    def _process_pdf_file(self, file_path: Path) -> List[Document]:
        """Process a PDF file into documents."""
        import pdfplumber
        
        documents = []
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    chunks = self._chunk_text(text)
                    
                    for i, chunk in enumerate(chunks):
                        if chunk.strip():
                            doc = Document(
                                id="",
                                text=chunk,
                                source=str(file_path),
                                page=page_num,
                                chunk_index=i,
                                metadata={
                                    'file_type': 'pdf',
                                    'chunk_size': len(chunk),
                                    'page_count': len(pdf.pages)
                                }
                            )
                            documents.append(doc)
        
        return documents
    
    def _chunk_text(self, text: str) -> List[str]:
        """Chunk text with overlap for better context preservation."""
        # Split into sentences first
        sentences = text.replace('\n', ' ').split('. ')
        sentences = [s.strip() + '.' for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = ""
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            
            # If adding this sentence exceeds chunk size, start new chunk
            if current_size + sentence_size > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Keep overlap by including last few sentences
                overlap_text = current_chunk.split('.')[-3:]  # Last 3 sentences
                current_chunk = '.'.join(overlap_text).strip()
                if current_chunk and not current_chunk.endswith('.'):
                    current_chunk += '.'
                current_chunk += ' ' + sentence
                current_size = len(current_chunk)
            else:
                current_chunk += ' ' + sentence if current_chunk else sentence
                current_size += sentence_size
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def retrieve(
        self,
        query: str,
        k: int = 5,
        use_reranking: bool = True,
        filters: Optional[Dict[str, Any]] = None,
        alpha: float = 0.7  # Favor semantic search
    ) -> Tuple[str, List[str], List[Document]]:
        """
        Retrieve relevant context with citations.
        
        Returns:
            - Combined context string
            - List of citations
            - List of source documents
        """
        # Search for relevant documents
        results = self.retriever.search(
            query=query,
            k=k,
            use_reranking=use_reranking,
            filters=filters,
            alpha=alpha
        )
        
        if not results:
            return "", [], []
        
        # Combine context and collect citations
        context_parts = []
        citations = []
        documents = []
        
        for doc, score in results:
            context_parts.append(f"[Relevance: {score:.2f}]\n{doc.text}")
            citation = doc.get_citation()
            if citation not in citations:
                citations.append(citation)
            documents.append(doc)
        
        combined_context = "\n\n---\n\n".join(context_parts)
        
        return combined_context, citations, documents
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the RAG system."""
        stats = {
            'total_documents': len(self.retriever.documents),
            'total_sources': len(set(doc.source for doc in self.retriever.documents)),
            'index_type': 'FAISS' if faiss and self.retriever.index else 'ChromaDB' if chromadb else 'NumPy',
            'has_sparse_index': self.retriever.bm25 is not None,
            'has_reranker': self.retriever.reranker is not None
        }
        
        # Source breakdown
        source_counts = {}
        for doc in self.retriever.documents:
            source_name = Path(doc.source).name
            source_counts[source_name] = source_counts.get(source_name, 0) + 1
        
        stats['source_breakdown'] = source_counts
        
        return stats 