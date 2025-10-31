# Knowledge Base Directory

Place your PDF documents here for the KAI Agent to learn from.

## Supported Content

- Technical documentation about photovoltaics
- Heat pump specifications and guides
- Economic analysis reports
- Installation manuals
- Market research documents
- Any domain-specific knowledge you want the agent to access

## How It Works

1. Place PDF files in this directory
2. On first run, the agent will:
   - Load all PDFs
   - Split them into chunks
   - Create embeddings with OpenAI
   - Build a FAISS vector index
3. The index is cached in `faiss_index/` for fast subsequent loads
4. Agent searches this knowledge base before using web search

## File Format

- **Supported**: PDF files only
- **Encoding**: UTF-8 recommended
- **Size**: No strict limit, but < 100MB per file recommended
- **Quantity**: Best performance with < 1000 files

## Example Files

You can add files like:

- `photovoltaik_grundlagen.pdf`
- `waermepumpen_technik.pdf`
- `amortisationsrechnung.pdf`
- `foerderungen_2024.pdf`

## Updating Knowledge Base

To update the knowledge base:

1. Add or remove PDF files
2. Delete the `faiss_index/` directory
3. Restart the application
4. Agent will rebuild the index automatically
