# Knowledge Base Directory

This directory contains PDF documents that the KAI Agent uses for knowledge retrieval and expert consulting.

## Current Documents

### 📄 photovoltaics_guide.pdf
Comprehensive guide on photovoltaic (PV) systems including:
- Technical specifications (module types, efficiency, power output)
- System components (modules, inverters, mounting, storage)
- Economic data (investment costs, ROI calculations, amortization)
- Benefits and advantages
- Installation requirements

### 📄 heatpump_guide.pdf
Comprehensive guide on heat pump systems including:
- Types of heat pumps (Luft-Wasser, Sole-Wasser, Wasser-Wasser)
- Technical specifications (JAZ ratings, efficiency)
- System components and operation
- Economic comparison with fossil fuel systems
- Installation requirements and permits
- Efficiency optimization tips

## How It Works

1. **Automatic Loading**: When the agent starts, it automatically scans this directory for PDF files
2. **Text Extraction**: PDFs are loaded and text is extracted from all pages
3. **Chunking**: Content is split into 800-character chunks with 150-character overlap
4. **Embedding**: OpenAI creates vector embeddings for semantic search
5. **Indexing**: FAISS builds a searchable vector index
6. **Caching**: Index is saved to `faiss_index/` to avoid reprocessing
7. **Search**: Agent can search for relevant information using natural language queries

## Adding Your Own Documents

To add your own knowledge documents:

1. **Add PDFs**: Place PDF files in this directory
2. **Restart Agent**: The agent will automatically detect and load new documents
3. **Rebuild Index**: The FAISS index will be rebuilt to include new content

### Supported Content

- Product specifications and datasheets
- Technical documentation
- Sales materials and brochures
- Installation guides
- Economic analyses and calculations
- Company policies and procedures
- FAQ documents

### Best Practices

- **Use Clear Text**: Ensure PDFs contain extractable text (not just images)
- **Organize Content**: Use clear headings and structure
- **Include Data**: Add specific numbers, specifications, and facts
- **Keep Updated**: Replace outdated documents with current versions
- **Reasonable Size**: Keep individual PDFs under 50 pages for optimal performance

## Requirements

- **OpenAI API Key**: Required for creating embeddings
- **FAISS**: Vector similarity search library (installed via requirements.txt)
- **PyPDF**: PDF text extraction library (installed via requirements.txt)

## Example Queries

Once the knowledge base is loaded, the agent can answer queries like:

- "Was sind die Vorteile von Photovoltaik?"
- "Wie hoch sind die Kosten für eine 10 kWp Solaranlage?"
- "Welche Wärmepumpentypen gibt es?"
- "Wie berechnet man die Amortisation?"
- "Was ist die JAZ einer Luft-Wasser-Wärmepumpe?"

## Troubleshooting

### No Documents Found
- Ensure PDF files are in this directory
- Check file extensions are `.pdf`
- Verify files are readable (not corrupted)

### Search Not Working
- Confirm `OPENAI_API_KEY` is set in `.env` file
- Check that FAISS index was created in `faiss_index/` directory
- Review logs for error messages

### Slow Performance
- Reduce number of documents
- Optimize chunk size in `knowledge_tools.py`
- Use index caching (enabled by default)

## Technical Details

- **Chunk Size**: 800 characters
- **Chunk Overlap**: 150 characters
- **Search Results**: Top 3 most relevant chunks
- **Embedding Model**: OpenAI text-embedding-ada-002
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Index Location**: `../faiss_index/`

## Maintenance

- **Update Documents**: Replace PDFs when information changes
- **Clear Cache**: Delete `faiss_index/` to force index rebuild
- **Monitor Size**: Keep total knowledge base under 1000 documents for best performance
- **Backup**: Regularly backup important documents

---

For more information, see the main Agent documentation in `Agent/README.md`
