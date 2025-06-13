"""Enhanced document processor with PDF support and citation tracking."""
import os
from pathlib import Path
from typing import List, Dict, Tuple
import re

try:
    import pdfplumber
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    pdfplumber = None
    TfidfVectorizer = None
    cosine_similarity = None

DOCUMENTS_PATH = Path('docs')


class DocumentChunk:
    """Represents a chunk of text from a document with metadata."""
    
    def __init__(self, text: str, source: str, page: int = None, chunk_id: int = None):
        self.text = text.strip()
        self.source = source
        self.page = page
        self.chunk_id = chunk_id
        
    def get_citation(self) -> str:
        """Generate citation for this chunk."""
        if self.page is not None:
            return f"[{Path(self.source).stem}, p. {self.page}]"
        else:
            return f"[{Path(self.source).stem}]"


class DocumentProcessor:
    """Enhanced document processor with PDF support and citation tracking."""
    
    def __init__(self, docs_path: Path = DOCUMENTS_PATH):
        self.docs_path = docs_path
        self.chunks_cache = {}
        self._all_chunks = []  # Flat list of all chunks for vector search
        self._load_documents()
        # Build TF-IDF index if sklearn is available and we have chunks
        if TfidfVectorizer and self._all_chunks:
            self._build_tfidf_index()
        else:
            self._vectorizer = None
            self._tfidf_matrix = None
    
    def _load_documents(self):
        """Load and process all documents in the docs directory."""
        if not self.docs_path.exists():
            print(f"Warning: Documents directory {self.docs_path} does not exist.")
            return
        
        # Process .txt files
        for txt_file in self.docs_path.glob('*.txt'):
            self._process_txt_file(txt_file)
        
        # Process .pdf files if pdfplumber is available
        if pdfplumber:
            for pdf_file in self.docs_path.glob('*.pdf'):
                self._process_pdf_file(pdf_file)
        else:
            pdf_files = list(self.docs_path.glob('*.pdf'))
            if pdf_files:
                print("Warning: PDF files found but pdfplumber not available. Install with: pip install pdfplumber")
    
    def _process_txt_file(self, file_path: Path):
        """Process a text file into chunks."""
        try:
            content = file_path.read_text(encoding='utf-8')
            # Split into paragraphs or chunks
            chunks = self._split_into_chunks(content)
            
            for i, chunk_text in enumerate(chunks):
                if chunk_text.strip():
                    chunk = DocumentChunk(
                        text=chunk_text,
                        source=str(file_path),
                        chunk_id=i
                    )
                    self._add_chunk_to_cache(chunk)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    def _process_pdf_file(self, file_path: Path):
        """Process a PDF file into chunks."""
        if not pdfplumber:
            return
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        # Split page text into chunks
                        chunks = self._split_into_chunks(text)
                        
                        for i, chunk_text in enumerate(chunks):
                            if chunk_text.strip():
                                chunk = DocumentChunk(
                                    text=chunk_text,
                                    source=str(file_path),
                                    page=page_num,
                                    chunk_id=i
                                )
                                self._add_chunk_to_cache(chunk)
        except Exception as e:
            print(f"Error processing PDF {file_path}: {e}")
    
    def _split_into_chunks(self, text: str, max_chunk_size: int = 400) -> List[str]:
        """Split text into smaller chunks for better retrieval."""
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # If adding this paragraph would exceed chunk size, start new chunk
            if current_chunk and len(current_chunk) + len(paragraph) > max_chunk_size:
                chunks.append(current_chunk)
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _add_chunk_to_cache(self, chunk: DocumentChunk):
        """Add a chunk to the cache for retrieval."""
        if not hasattr(self, 'chunks_cache'):
            self.chunks_cache = {}
        
        source_key = Path(chunk.source).stem
        if source_key not in self.chunks_cache:
            self.chunks_cache[source_key] = []
        
        self.chunks_cache[source_key].append(chunk)
        self._all_chunks.append(chunk)
    
    def _build_tfidf_index(self):
        texts = [c.text for c in self._all_chunks]
        self._vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
        self._tfidf_matrix = self._vectorizer.fit_transform(texts)
    
    def _vector_retrieval(self, query: str, top_k: int = 5):
        if self._vectorizer is None or self._tfidf_matrix is None:
            return []
        q_vec = self._vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self._tfidf_matrix)[0]
        top_idx = sims.argsort()[-top_k:][::-1]
        return [(self._all_chunks[i], sims[i]) for i in top_idx if sims[i] > 0]
    
    def retrieve_context_with_citations(self, query: str, max_chunks: int = 5, max_chars: int = 6000) -> Tuple[str, List[str]]:
        """
        Retrieve relevant context chunks with citations.
        
        Returns:
            Tuple of (combined_context, list_of_citations)
        """
        relevant_chunks = []
        query_lower = query.lower()
        
        if self._vectorizer:
            relevant_chunks = self._vector_retrieval(query, top_k=max_chunks*2)  # get extra then truncate later
        else:
            # Search through all chunks
            for source, chunks in self.chunks_cache.items():
                for chunk in chunks:
                    # Simple relevance scoring based on keyword matching
                    text_lower = chunk.text.lower()
                    relevance_score = 0
                    
                    # Count keyword matches
                    query_words = query_lower.split()
                    for word in query_words:
                        if len(word) > 2:  # Skip very short words
                            relevance_score += text_lower.count(word)
                    
                    if relevance_score > 0:
                        relevant_chunks.append((chunk, relevance_score))
        
        # Sort by relevance score and take top chunks
        relevant_chunks.sort(key=lambda x: x[1], reverse=True)
        top_chunks = relevant_chunks[:max_chunks]
        
        if not top_chunks:
            return "", []
        
        # Combine context and collect citations
        context_parts = []
        citations = []
        
        for chunk, score in top_chunks:
            context_parts.append(chunk.text)
            citation = chunk.get_citation()
            if citation not in citations:
                citations.append(citation)
        
        combined_context = "\n\n".join(context_parts)
        # Truncate if too long
        if len(combined_context) > max_chars:
            combined_context = combined_context[:max_chars] + "..."
        return combined_context, citations
    
    def get_available_sources(self) -> List[str]:
        """Get list of available document sources."""
        return list(self.chunks_cache.keys())
    
    def search_specific_source(self, source_name: str, query: str) -> Tuple[str, List[str]]:
        """Search within a specific document source."""
        if source_name not in self.chunks_cache:
            return "", []
        
        relevant_chunks = []
        query_lower = query.lower()
        
        for chunk in self.chunks_cache[source_name]:
            text_lower = chunk.text.lower()
            if query_lower in text_lower:
                # Calculate simple relevance score
                score = text_lower.count(query_lower)
                relevant_chunks.append((chunk, score))
        
        # Sort by relevance
        relevant_chunks.sort(key=lambda x: x[1], reverse=True)
        
        if not relevant_chunks:
            return "", []
        
        # Take top 3 chunks from this source
        top_chunks = relevant_chunks[:3]
        context_parts = []
        citations = []
        
        for chunk, score in top_chunks:
            context_parts.append(chunk.text)
            citation = chunk.get_citation()
            if citation not in citations:
                citations.append(citation)
        
        return "\n\n".join(context_parts), citations


# Global document processor instance
doc_processor = DocumentProcessor()


def retrieve_context_with_citations(topic: str) -> Tuple[str, List[str]]:
    """
    Retrieve context with citations for a given topic.
    
    Returns:
        Tuple of (context_text, list_of_citations)
    """
    return doc_processor.retrieve_context_with_citations(topic)


def get_available_sources() -> List[str]:
    """Get list of available document sources."""
    return doc_processor.get_available_sources()


def search_in_source(source_name: str, query: str) -> Tuple[str, List[str]]:
    """Search within a specific document source."""
    return doc_processor.search_specific_source(source_name, query) 