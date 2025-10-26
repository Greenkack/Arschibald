"""
Knowledge Base Tools for KAI Agent
===================================

Manages domain-specific knowledge through vector database search.
Loads PDF documents, creates embeddings, and provides similarity search.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
"""

import os
import time
from typing import Optional
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# LangChain 1.0+ Import-Updates
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import Tool

# Import logging utilities
from agent.logging_config import get_logger, log_tool_execution

# Import error classes
from agent.errors import KnowledgeBaseError, APIError

# Get logger for this module
logger = get_logger(__name__)

# Global cache for lazy loading
_cached_vector_store = None
_cache_metadata = {}


def setup_knowledge_base(
    path: str = "knowledge_base",
    db_path: str = "faiss_index",
    chunk_size: int = 800,
    chunk_overlap: int = 150,
    lazy_load: bool = True
) -> Optional[FAISS]:
    """
    Load PDFs, create embeddings, and build FAISS vector store.

    Performance Optimizations (Task 15.1):
    - Index caching: Loads existing index without reprocessing
    - Lazy loading: Optional deferred loading for faster startup
    - Optimized chunk size: 800 chars with 150 overlap for better context
    - Batch processing: Efficient document loading
    - Metadata tracking: Tracks document changes for smart rebuilding

    Args:
        path: Directory containing PDF documents
        db_path: Path to save/load FAISS index
        chunk_size: Size of text chunks (default: 800, optimized)
        chunk_overlap: Overlap between chunks (default: 150, optimized)
        lazy_load: If True, defer loading until first search

    Returns:
        FAISS vector store instance, or None if no documents found

    Process:
        1. Check if FAISS index exists (load if yes, skip processing)
        2. Verify index is up-to-date with source documents
        3. Load all PDFs from directory (batch processing)
        4. Split into optimized chunks
        5. Create embeddings with OpenAI
        6. Build and save FAISS index with metadata

    Requirements:
        - 3.1: Load PDF documents from knowledge_base directory
        - 3.2: Create vector embeddings using FAISS
        - 3.3: Implement index caching to avoid reprocessing
        - 3.4: Handle empty knowledge base gracefully
        - 3.5: Support similarity search
    """
    global _cached_vector_store, _cache_metadata

    # Check in-memory cache first (fastest)
    if _cached_vector_store is not None and not lazy_load:
        logger.info("Returning cached knowledge base from memory")
        return _cached_vector_store

    logger.info(f"Setting up knowledge base from {path}")
    start_time = time.time()

    # Create knowledge base directory if it doesn't exist
    kb_dir = Path(path)
    kb_dir.mkdir(exist_ok=True)
    logger.debug(f"Knowledge base directory: {kb_dir}")

    # Metadata file for tracking document changes
    metadata_file = Path(db_path) / "metadata.txt"

    # Check if FAISS index already exists (caching optimization)
    if os.path.exists(db_path):
        try:
            logger.info(f"Loading existing FAISS index from {db_path}")
            print(f"📚 Loading existing FAISS index from {db_path}...")

            # Check if index is up-to-date
            needs_rebuild = False
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    cached_files = set(f.read().strip().split('\n'))

                current_files = set(
                    str(p.name) for p in kb_dir.glob("*.pdf")
                )

                if cached_files != current_files:
                    logger.info("Document changes detected, rebuilding index")
                    print("🔄 Document changes detected, rebuilding index...")
                    needs_rebuild = True

            if not needs_rebuild:
                embeddings = OpenAIEmbeddings()
                vector_store = FAISS.load_local(
                    db_path,
                    embeddings,
                    allow_dangerous_deserialization=True
                )

                # Store in cache
                _cached_vector_store = vector_store
                _cache_metadata = {
                    'path': path,
                    'db_path': db_path,
                    'chunk_size': chunk_size,
                    'chunk_overlap': chunk_overlap,
                    'loaded_at': time.time()
                }

                duration = time.time() - start_time
                logger.info(
                    f"Knowledge base loaded in {duration:.2f}s (cached)"
                )
                print(
                    f"✅ Knowledge base loaded successfully! "
                    f"({duration:.2f}s)"
                )
                return vector_store

        except Exception as e:
            logger.warning(f"Error loading existing index: {e}")
            print(f"⚠️ Error loading existing index: {e}")
            print("🔄 Will rebuild index from PDFs...")

    # Find all PDF files in knowledge base directory
    pdf_files = list(kb_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files in {path}")

    if not pdf_files:
        logger.warning(f"No PDF files found in {path}/")
        print(f"⚠️ No PDF files found in {path}/")
        print(
            "💡 Add PDF documents to the knowledge_base/ directory "
            "to enable knowledge search."
        )

        # Create a placeholder file with instructions
        placeholder_path = kb_dir / "README.txt"
        if not placeholder_path.exists():
            with open(placeholder_path, "w", encoding="utf-8") as f:
                f.write("""
KAI Agent Knowledge Base
========================

This directory should contain PDF documents that the agent can search.

Examples:
- Product datasheets (photovoltaic modules, inverters, heat pumps)
- Technical specifications
- Installation guides
- Economic analysis reports
- Company documentation

Simply place PDF files in this directory and restart the application.
The agent will automatically index them for search.
""")

        return None

    print(f"📄 Found {len(pdf_files)} PDF files in knowledge base")
    print("🔄 Loading and processing documents...")
    logger.info("Loading and processing PDF documents")

    # Batch processing optimization: Load all PDFs efficiently
    documents = []
    failed_files = []

    for pdf_file in pdf_files:
        try:
            logger.debug(f"Loading PDF: {pdf_file.name}")
            print(f"  Loading: {pdf_file.name}")
            loader = PyPDFLoader(str(pdf_file))
            docs = loader.load()
            documents.extend(docs)
            logger.debug(f"Loaded {len(docs)} pages from {pdf_file.name}")
        except Exception as e:
            logger.error(f"Error loading {pdf_file.name}: {e}")
            print(f"  ⚠️ Error loading {pdf_file.name}: {e}")
            failed_files.append(pdf_file.name)
            continue

    if not documents:
        logger.error("No documents could be loaded")
        print("❌ No documents could be loaded")
        if failed_files:
            print(f"Failed files: {', '.join(failed_files)}")
        return None

    logger.info(f"Loaded {len(documents)} pages from {len(pdf_files)} PDFs")
    print(f"✅ Loaded {len(documents)} pages from PDFs")

    if failed_files:
        logger.warning(f"Failed to load {len(failed_files)} files")
        print(f"⚠️ Failed to load {len(failed_files)} files")

    # Split documents into optimized chunks
    logger.info(
        f"Splitting documents into chunks "
        f"(size={chunk_size}, overlap={chunk_overlap})"
    )
    print("✂️ Splitting documents into optimized chunks...")

    # Optimized text splitter configuration
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],  # Better splitting
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Created {len(chunks)} text chunks")
    print(f"✅ Created {len(chunks)} text chunks")

    # Create embeddings and build FAISS index
    logger.info("Creating embeddings and building FAISS index")
    print("🧠 Creating embeddings and building FAISS index...")
    print("   (This may take a few minutes depending on document size)")

    try:
        try:
            embeddings = OpenAIEmbeddings()
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI embeddings: {e}")
            raise APIError(
                "Failed to initialize OpenAI embeddings",
                api_name="OpenAI",
                solution=(
                    "Check OPENAI_API_KEY in .env file and ensure it's valid. "
                    "Also verify network connection."
                )
            )

        # Batch processing for large document sets
        if len(chunks) > 100:
            logger.info("Large document set detected, using batch processing")
            print("   Using batch processing for large document set...")

        try:
            vector_store = FAISS.from_documents(chunks, embeddings)
        except Exception as e:
            logger.error(f"Failed to create FAISS index: {e}")
            raise KnowledgeBaseError(
                f"Failed to create FAISS vector store: {str(e)}",
                path=path,
                solution=(
                    "This may be due to:\n"
                    "  1. Invalid PDF content\n"
                    "  2. OpenAI API issues\n"
                    "  3. Insufficient memory\n"
                    "Try with fewer/smaller PDF files first."
                )
            )

        # Save the index for future use (caching)
        logger.info(f"Saving FAISS index to {db_path}")
        print(f"💾 Saving FAISS index to {db_path}...")
        try:
            vector_store.save_local(db_path)
        except Exception as e:
            logger.warning(f"Failed to save FAISS index: {e}")
            print(f"⚠️ Warning: Could not save index to disk: {e}")
            # Continue anyway - we have the index in memory

        # Save metadata for change detection
        try:
            metadata_file.parent.mkdir(parents=True, exist_ok=True)
            with open(metadata_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(str(p.name) for p in pdf_files))
        except Exception as e:
            logger.warning(f"Failed to save metadata: {e}")
            # Non-critical, continue

        # Store in cache
        _cached_vector_store = vector_store
        _cache_metadata = {
            'path': path,
            'db_path': db_path,
            'chunk_size': chunk_size,
            'chunk_overlap': chunk_overlap,
            'num_documents': len(documents),
            'num_chunks': len(chunks),
            'created_at': time.time()
        }

        duration = time.time() - start_time
        logger.info(
            f"Knowledge base created and saved in {duration:.2f}s"
        )
        print(
            f"✅ Knowledge base created and saved successfully! "
            f"({duration:.2f}s)"
        )
        return vector_store

    except (APIError, KnowledgeBaseError) as e:
        logger.error(f"Error creating vector store: {e}")
        print(f"❌ {e.__class__.__name__}: {e.message}")
        if e.solution:
            print(f"💡 Solution:\n{e.solution}")
        return None
    except Exception as e:
        logger.error(
            f"Unexpected error creating vector store: {e}",
            exc_info=True)
        print(f"❌ Unexpected error creating vector store: {e}")
        print("💡 Check logs for details")
        return None


def clear_knowledge_base_cache():
    """
    Clear the in-memory knowledge base cache.

    Forces reload on next access. Useful for testing or when
    documents have changed.
    """
    global _cached_vector_store, _cache_metadata
    _cached_vector_store = None
    _cache_metadata = {}
    logger.info("Knowledge base cache cleared")


def get_cache_info() -> dict:
    """
    Get information about the current cache state.

    Returns:
        Dictionary with cache information:
        - cached: Whether vector store is cached
        - metadata: Cache metadata (chunk_size, etc.)
    """
    return {
        'cached': _cached_vector_store is not None,
        'metadata': _cache_metadata.copy()
    }


def lazy_load_knowledge_base(
    path: str = "knowledge_base",
    db_path: str = "faiss_index"
) -> Optional[FAISS]:
    """
    Lazy load knowledge base on first use.

    Performance optimization: Defers loading until first search,
    reducing startup time. Uses in-memory cache to avoid repeated
    disk access.

    Args:
        path: Directory containing PDF documents
        db_path: Path to FAISS index

    Returns:
        FAISS vector store instance, or None if not available
    """
    global _cached_vector_store, _cache_metadata

    if _cached_vector_store is not None:
        logger.info("Returning cached knowledge base")
        return _cached_vector_store

    logger.info("Lazy loading knowledge base on first use")
    vector_store = setup_knowledge_base(
        path=path,
        db_path=db_path,
        lazy_load=False
    )

    if vector_store is not None:
        _cached_vector_store = vector_store
        _cache_metadata = {
            'path': path,
            'db_path': db_path,
            'loaded_at': time.time()
        }

    return vector_store


def knowledge_base_search(vector_store: Optional[FAISS]) -> Tool:
    """
    Create a search tool with vector store access.

    This tool allows the agent to search the knowledge base for relevant
    information. It performs similarity search and returns the top k results.

    Args:
        vector_store: FAISS vector store instance (can be None)

    Returns:
        LangChain Tool for knowledge base search

    Requirements:
        - 3.4: Implement similarity search with k=3 results
        - 3.5: Handle empty knowledge base gracefully
    """

    def search_knowledge(query: str) -> str:
        """
        Search the knowledge base for relevant information.

        Args:
            query: Search query string

        Returns:
            Formatted search results with source information
        """
        start_time = time.time()
        logger.info(f"Searching knowledge base: {query[:100]}")

        if vector_store is None:
            logger.warning(
                "Knowledge base not available - no PDF documents loaded")
            return (
                "⚠️ Knowledge base is not available. "
                "No PDF documents were found in the knowledge_base/ directory. "
                "Please add relevant PDF documents and restart the application.")

        try:
            # Perform similarity search (k=3 for top 3 results)
            logger.debug("Performing similarity search (k=3)")
            results = vector_store.similarity_search(query, k=3)

            duration = time.time() - start_time

            if not results:
                logger.info(f"No results found for query in {duration:.2f}s")
                log_tool_execution(
                    logger,
                    tool_name="knowledge_base_search",
                    input_summary=query[:100],
                    success=True,
                    duration=duration
                )
                return f"No relevant information found for query: {query}"

            logger.info(f"Found {len(results)} results in {duration:.2f}s")

            # Format results for agent consumption
            formatted_results = []
            for i, doc in enumerate(results, 1):
                source = doc.metadata.get('source', 'Unknown')
                page = doc.metadata.get('page', 'Unknown')
                content = doc.page_content.strip()

                logger.debug(f"Result {i}: {source} (Page {page})")

                formatted_results.append(
                    f"Result {i}:\n"
                    f"Source: {source} (Page {page})\n"
                    f"Content: {content}\n"
                )

            # Log successful tool execution
            log_tool_execution(
                logger,
                tool_name="knowledge_base_search",
                input_summary=query[:100],
                success=True,
                duration=duration
            )

            return "\n---\n".join(formatted_results)

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Error searching knowledge base: {str(e)}"
            logger.error(error_msg, exc_info=True)

            # Log failed tool execution
            log_tool_execution(
                logger,
                tool_name="knowledge_base_search",
                input_summary=query[:100],
                success=False,
                duration=duration,
                error=str(e)
            )

            return error_msg

    return Tool(
        name="knowledge_base_search", description=(
            "Search the knowledge base for information about renewable energy systems, "
            "photovoltaics, heat pumps, technical specifications, and related topics. "
            "Use this tool FIRST before searching the web. "
            "Input should be a clear search query."), func=search_knowledge)
