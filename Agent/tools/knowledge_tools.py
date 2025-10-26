"""
Knowledge Base Tools for KAI Agent
===================================

Manages domain-specific knowledge through vector database search.
Loads PDF documents, creates embeddings, and provides similarity search.
"""

import os
from typing import Optional
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools import Tool


def setup_knowledge_base(
    path: str = "knowledge_base",
    db_path: str = "faiss_index",
    chunk_size: int = 1000,
    chunk_overlap: int = 100
) -> Optional[FAISS]:
    """
    Load PDFs, create embeddings, and build FAISS vector store.

    This function implements intelligent caching - if the FAISS index already
    exists, it loads it directly without reprocessing documents. This significantly
    improves startup time.

    Args:
        path: Directory containing PDF documents
        db_path: Path to save/load FAISS index
        chunk_size: Size of text chunks for splitting (default: 1000)
        chunk_overlap: Overlap between chunks (default: 100)

    Returns:
        FAISS vector store instance, or None if no documents found

    Process:
        1. Check if FAISS index exists (load if yes, skip processing)
        2. Load all PDFs from directory
        3. Split into chunks using RecursiveCharacterTextSplitter
        4. Create embeddings with OpenAI
        5. Build and save FAISS index

    Requirements:
        - 3.1: Load PDF documents from knowledge_base directory
        - 3.2: Create vector embeddings using FAISS
        - 3.3: Implement index caching to avoid reprocessing
        - 3.4: Handle empty knowledge base gracefully
        - 3.5: Support similarity search
    """
    # Create knowledge base directory if it doesn't exist
    kb_dir = Path(path)
    kb_dir.mkdir(exist_ok=True)

    # Check if FAISS index already exists (caching)
    if os.path.exists(db_path):
        try:
            print(f"📚 Loading existing FAISS index from {db_path}...")
            embeddings = OpenAIEmbeddings()
            vector_store = FAISS.load_local(
                db_path,
                embeddings,
                allow_dangerous_deserialization=True
            )
            print(f"✅ Knowledge base loaded successfully!")
            return vector_store
        except Exception as e:
            print(f"⚠️ Error loading existing index: {e}")
            print("🔄 Will rebuild index from PDFs...")

    # Find all PDF files in knowledge base directory
    pdf_files = list(kb_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"⚠️ No PDF files found in {path}/")
        print("💡 Add PDF documents to the knowledge_base/ directory to enable knowledge search.")

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

    # Load all PDF documents
    documents = []
    for pdf_file in pdf_files:
        try:
            print(f"  Loading: {pdf_file.name}")
            loader = PyPDFLoader(str(pdf_file))
            docs = loader.load()
            documents.extend(docs)
        except Exception as e:
            print(f"  ⚠️ Error loading {pdf_file.name}: {e}")
            continue

    if not documents:
        print("❌ No documents could be loaded")
        return None

    print(f"✅ Loaded {len(documents)} pages from PDFs")

    # Split documents into chunks
    print("✂️ Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Created {len(chunks)} text chunks")

    # Create embeddings and build FAISS index
    print("🧠 Creating embeddings and building FAISS index...")
    print("   (This may take a few minutes depending on document size)")

    try:
        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.from_documents(chunks, embeddings)

        # Save the index for future use (caching)
        print(f"💾 Saving FAISS index to {db_path}...")
        vector_store.save_local(db_path)

        print("✅ Knowledge base created and saved successfully!")
        return vector_store

    except Exception as e:
        print(f"❌ Error creating vector store: {e}")
        return None


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
        if vector_store is None:
            return (
                "⚠️ Knowledge base is not available. "
                "No PDF documents were found in the knowledge_base/ directory. "
                "Please add relevant PDF documents and restart the application.")

        try:
            # Perform similarity search (k=3 for top 3 results)
            results = vector_store.similarity_search(query, k=3)

            if not results:
                return f"No relevant information found for query: {query}"

            # Format results for agent consumption
            formatted_results = []
            for i, doc in enumerate(results, 1):
                source = doc.metadata.get('source', 'Unknown')
                page = doc.metadata.get('page', 'Unknown')
                content = doc.page_content.strip()

                formatted_results.append(
                    f"Result {i}:\n"
                    f"Source: {source} (Page {page})\n"
                    f"Content: {content}\n"
                )

            return "\n---\n".join(formatted_results)

        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"

    return Tool(
        name="knowledge_base_search", description=(
            "Search the knowledge base for information about renewable energy systems, "
            "photovoltaics, heat pumps, technical specifications, and related topics. "
            "Use this tool FIRST before searching the web. "
            "Input should be a clear search query."), func=search_knowledge)
