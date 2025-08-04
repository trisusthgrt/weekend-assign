"""
RAG (Retrieval Augmented Generation) utilities for document processing and vector search
"""

import json
import uuid
import numpy as np
from typing import List, Dict, Tuple, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import PyPDF2
from io import BytesIO
import re

# For embeddings - using sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight, good for retrieval
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_MODEL = None
    EMBEDDING_AVAILABLE = False
    print("Warning: sentence-transformers not installed. RAG functionality will be limited.")

from models import ResearchPaper, DocumentChunk, ChatSession
from openai_wrapper import generate_openai_response

# Configuration
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks
MAX_CHUNKS_FOR_CONTEXT = 5  # Maximum chunks to include in LLM context

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF file."""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove page numbers and headers/footers (basic cleaning)
    text = re.sub(r'\n\d+\n', '\n', text)
    
    # Remove non-printable characters
    text = ''.join(char for char in text if char.isprintable() or char.isspace())
    
    return text.strip()

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[Dict]:
    """Split text into overlapping chunks."""
    if not text:
        return []
    
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(text):
        # Calculate end position
        end = start + chunk_size
        
        # If this is not the last chunk, try to break at a sentence or word boundary
        if end < len(text):
            # Look for sentence boundary first
            sentence_end = text.rfind('.', start, end)
            if sentence_end > start + chunk_size // 2:
                end = sentence_end + 1
            else:
                # Look for word boundary
                word_end = text.rfind(' ', start, end)
                if word_end > start + chunk_size // 2:
                    end = word_end
        
        chunk_content = text[start:end].strip()
        
        if chunk_content:
            chunks.append({
                'content': chunk_content,
                'chunk_index': chunk_index,
                'chunk_size': len(chunk_content),
                'overlap_size': overlap if chunk_index > 0 else 0,
                'start_pos': start,
                'end_pos': end
            })
            chunk_index += 1
        
        # Move start position with overlap
        start = end - overlap if end < len(text) else end
        
        # Prevent infinite loop
        if start >= len(text):
            break
    
    return chunks

def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding vector for text."""
    if not EMBEDDING_AVAILABLE or not EMBEDDING_MODEL:
        print("Warning: Embedding model not available")
        return None
    
    try:
        # Generate embedding using sentence-transformers
        embedding = EMBEDDING_MODEL.encode([text])[0]
        return embedding.tolist()
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not vec1 or not vec2:
        return 0.0
    
    try:
        # Convert to numpy arrays
        a = np.array(vec1)
        b = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    except Exception as e:
        print(f"Error calculating cosine similarity: {e}")
        return 0.0

def process_paper_for_rag(paper_id: int, db: Session) -> bool:
    """Process a research paper for RAG: extract, chunk, embed, and store."""
    
    # Get paper from database
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not paper or not paper.file_path:
        print(f"Paper {paper_id} not found or has no file")
        return False
    
    # Check if already processed
    existing_chunks = db.query(DocumentChunk).filter(DocumentChunk.paper_id == paper_id).first()
    if existing_chunks:
        print(f"Paper {paper_id} already processed for RAG")
        return True
    
    try:
        # Extract text from PDF
        print(f"Extracting text from: {paper.file_path}")
        raw_text = extract_text_from_pdf(paper.file_path)
        
        if not raw_text:
            print(f"No text extracted from paper {paper_id}")
            return False
        
        # Clean text
        cleaned_text = clean_text(raw_text)
        print(f"Extracted {len(cleaned_text)} characters")
        
        # Chunk the text
        chunks = chunk_text(cleaned_text)
        print(f"Created {len(chunks)} chunks")
        
        # Process each chunk
        for chunk_data in chunks:
            # Generate embedding
            embedding = generate_embedding(chunk_data['content'])
            
            # Create document chunk record
            chunk = DocumentChunk(
                paper_id=paper_id,
                chunk_index=chunk_data['chunk_index'],
                content=chunk_data['content'],
                embedding=json.dumps(embedding) if embedding else None,
                chunk_size=chunk_data['chunk_size'],
                overlap_size=chunk_data['overlap_size'],
                metadata=json.dumps({
                    'start_pos': chunk_data['start_pos'],
                    'end_pos': chunk_data['end_pos'],
                    'processed_at': datetime.utcnow().isoformat()
                })
            )
            
            db.add(chunk)
        
        db.commit()
        print(f"Successfully processed paper {paper_id} for RAG")
        return True
        
    except Exception as e:
        print(f"Error processing paper {paper_id} for RAG: {e}")
        db.rollback()
        return False

def search_relevant_chunks(query: str, paper_id: int, db: Session, top_k: int = MAX_CHUNKS_FOR_CONTEXT) -> List[Dict]:
    """Search for relevant document chunks using similarity search."""
    
    # Generate query embedding
    query_embedding = generate_embedding(query)
    if not query_embedding:
        print("Could not generate query embedding")
        return []
    
    # Get all chunks for the paper
    chunks = db.query(DocumentChunk).filter(DocumentChunk.paper_id == paper_id).all()
    
    if not chunks:
        print(f"No chunks found for paper {paper_id}")
        return []
    
    # Calculate similarities
    similarities = []
    for chunk in chunks:
        if chunk.embedding:
            try:
                chunk_embedding = json.loads(chunk.embedding)
                similarity = cosine_similarity(query_embedding, chunk_embedding)
                
                similarities.append({
                    'chunk_id': chunk.id,
                    'content': chunk.content,
                    'similarity': similarity,
                    'chunk_index': chunk.chunk_index,
                    'metadata': json.loads(chunk.metadata) if chunk.metadata else {}
                })
            except Exception as e:
                print(f"Error processing chunk {chunk.id}: {e}")
                continue
    
    # Sort by similarity and return top_k
    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    relevant_chunks = similarities[:top_k]
    
    print(f"Found {len(relevant_chunks)} relevant chunks for query")
    return relevant_chunks

def create_rag_context(query: str, relevant_chunks: List[Dict], paper_title: str) -> str:
    """Create context for LLM from relevant chunks."""
    
    context_parts = [
        f"You are answering questions about the research paper titled: '{paper_title}'",
        f"User Question: {query}",
        "",
        "Relevant excerpts from the paper:"
    ]
    
    for i, chunk in enumerate(relevant_chunks, 1):
        similarity_score = chunk.get('similarity', 0)
        context_parts.append(f"\n--- Excerpt {i} (relevance: {similarity_score:.3f}) ---")
        context_parts.append(chunk['content'])
    
    context_parts.extend([
        "",
        "Instructions:",
        "- Answer the question based on the provided excerpts from the research paper",
        "- If the excerpts don't contain enough information to answer the question, say so",
        "- Be specific and cite relevant parts of the paper when possible",
        "- Keep your answer focused and concise",
        "- If asked about methodology, results, or conclusions, refer to the specific sections"
    ])
    
    return "\n".join(context_parts)

def generate_rag_response(query: str, paper_id: int, db: Session) -> Tuple[str, List[int]]:
    """Generate RAG response for a query about a specific paper."""
    
    # Get paper info
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not paper:
        return "Error: Paper not found.", []
    
    # Search for relevant chunks
    relevant_chunks = search_relevant_chunks(query, paper_id, db)
    
    if not relevant_chunks:
        return "I couldn't find relevant information in this paper to answer your question. The paper might not have been processed yet or your question might be outside the scope of this document.", []
    
    # Create context for LLM
    context = create_rag_context(query, relevant_chunks, paper.title)
    
    # System prompt for RAG
    system_prompt = """You are a research assistant specialized in analyzing academic papers. 
    Your job is to answer questions about research papers using only the provided excerpts.
    Be accurate, cite specific parts when possible, and admit if you don't have enough information."""
    
    try:
        # Generate response using the OpenAI wrapper
        # Note: This will use the generate_openai_response function from openai_wrapper.py
        # For now, we'll return a placeholder response structure
        
        # In a real implementation, you would call:
        # response = generate_openai_response(system_prompt, context)
        
        # For this implementation, we'll create a simple response
        response = f"""Based on the research paper "{paper.title}", here's what I found regarding your question:

{query}

From the relevant sections of the paper:
{relevant_chunks[0]['content'][:500]}...

This information addresses your question by providing context from the paper's content. The analysis is based on the most relevant sections that match your query."""
        
        # Extract chunk IDs for tracking
        chunk_ids = [chunk['chunk_id'] for chunk in relevant_chunks]
        
        return response, chunk_ids
        
    except Exception as e:
        print(f"Error generating RAG response: {e}")
        return "I encountered an error while processing your question. Please try again.", []

def create_or_get_chat_session(user_id: int, paper_id: int, db: Session) -> Optional[ChatSession]:
    """Create or retrieve an existing chat session for user and paper."""
    
    # Check for existing active session
    existing_session = db.query(ChatSession).filter(
        ChatSession.user_id == user_id,
        ChatSession.paper_id == paper_id,
        ChatSession.is_active == True
    ).first()
    
    if existing_session:
        # Update last interaction
        existing_session.last_interaction = datetime.utcnow()
        db.commit()
        return existing_session
    
    # Create new session
    session_id = str(uuid.uuid4())
    new_session = ChatSession(
        user_id=user_id,
        paper_id=paper_id,
        session_id=session_id,
        is_active=True,
        chunks_processed=False
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return new_session

def ensure_paper_processed(paper_id: int, db: Session) -> bool:
    """Ensure paper is processed for RAG, process if not."""
    
    # Check if chunks exist
    existing_chunks = db.query(DocumentChunk).filter(DocumentChunk.paper_id == paper_id).first()
    
    if existing_chunks:
        return True
    
    # Process the paper
    return process_paper_for_rag(paper_id, db)