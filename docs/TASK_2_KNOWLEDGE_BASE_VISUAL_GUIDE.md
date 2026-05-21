# Task 2: Knowledge Base System - Visual Guide

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Knowledge Base System                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     knowledge_base/ Directory           │
        │  ┌───────────────────────────────────┐  │
        │  │  • product_datasheet_1.pdf        │  │
        │  │  • technical_specs.pdf            │  │
        │  │  • installation_guide.pdf         │  │
        │  │  • economic_analysis.pdf          │  │
        │  └───────────────────────────────────┘  │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │    setup_knowledge_base()               │
        │                                         │
        │  1. Check for existing FAISS index     │
        │     ├─ Yes → Load cached index         │
        │     └─ No → Process PDFs               │
        │                                         │
        │  2. Load PDFs with PyPDFLoader         │
        │  3. Split into chunks (1000/100)       │
        │  4. Create OpenAI embeddings           │
        │  5. Build FAISS vector store           │
        │  6. Save index for future use          │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │      FAISS Vector Store                 │
        │                                         │
        │  ┌───────────────────────────────────┐  │
        │  │  Chunk 1: [embedding vector]      │  │
        │  │  Chunk 2: [embedding vector]      │  │
        │  │  Chunk 3: [embedding vector]      │  │
        │  │  ...                              │  │
        │  │  Chunk N: [embedding vector]      │  │
        │  └───────────────────────────────────┘  │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │   knowledge_base_search() Tool          │
        │                                         │
        │  Input: "photovoltaic efficiency"      │
        │         ↓                               │
        │  Similarity Search (k=3)                │
        │         ↓                               │
        │  Output: Top 3 relevant chunks          │
        │          with source & page info        │
        └─────────────────────────────────────────┘
```

## Data Flow

```
PDF Documents
     ↓
PyPDFLoader
     ↓
Raw Text Pages
     ↓
RecursiveCharacterTextSplitter
     ↓
Text Chunks (1000 chars, 100 overlap)
     ↓
OpenAI Embeddings API
     ↓
Vector Embeddings (1536 dimensions)
     ↓
FAISS Index
     ↓
Saved to Disk (faiss_index/)
     ↓
Loaded on Startup (cached)
     ↓
Available for Similarity Search
```

## Search Process

```
User Query: "What are the benefits of photovoltaic systems?"
                              │
                              ▼
                    Convert to Embedding
                              │
                              ▼
                    FAISS Similarity Search
                              │
                              ▼
                    Find Top 3 Closest Vectors
                              │
                              ▼
        ┌─────────────────────┴─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
   Result 1              Result 2              Result 3
   ────────              ────────              ────────
   Source: spec.pdf      Source: guide.pdf     Source: spec.pdf
   Page: 5               Page: 12              Page: 7
   Content: "PV         Content: "Solar       Content: "Benefits
   systems reduce..."    panels provide..."    include reduced..."
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                              ▼
                    Formatted Response
                              │
                              ▼
                    Returned to Agent
```

## File Structure

```
Bokuk2/
├── knowledge_base/              # PDF documents directory
│   ├── README.txt              # Auto-generated instructions
│   ├── product_datasheet.pdf   # Example PDF
│   └── technical_specs.pdf     # Example PDF
│
├── faiss_index/                # Cached vector store
│   ├── index.faiss            # FAISS index file
│   └── index.pkl              # Metadata pickle
│
├── agent/
│   └── agent/
│       └── tools/
│           ├── __init__.py
│           └── knowledge_tools.py  # Implementation
│
└── test_knowledge_base.py      # Test script
```

## Caching Mechanism

```
First Run:
──────────
1. Check faiss_index/ → Not found
2. Load all PDFs from knowledge_base/
3. Process documents (takes time)
4. Create embeddings (API calls)
5. Build FAISS index
6. Save to faiss_index/
7. Return vector store

Subsequent Runs:
────────────────
1. Check faiss_index/ → Found!
2. Load existing index (fast)
3. Skip PDF processing
4. Skip embedding creation
5. Return vector store

Time Saved: ~90% faster startup
```

## Error Handling Flow

```
setup_knowledge_base()
        │
        ├─ No PDFs found?
        │  └─ Create README.txt with instructions
        │     Return None
        │
        ├─ PDF loading error?
        │  └─ Skip that PDF, continue with others
        │     Log warning
        │
        ├─ Embedding API error?
        │  └─ Catch exception
        │     Log error
        │     Return None
        │
        └─ Success
           └─ Return vector store

knowledge_base_search()
        │
        ├─ Vector store is None?
        │  └─ Return helpful error message
        │
        ├─ Search error?
        │  └─ Catch exception
        │     Return error message
        │
        └─ Success
           └─ Return formatted results
```

## Usage in Agent Context

```
Agent Initialization:
─────────────────────
1. Load configuration
2. Setup knowledge base
   vector_store = setup_knowledge_base()
3. Create search tool
   search_tool = knowledge_base_search(vector_store)
4. Register tool with agent
   tools = [search_tool, ...]
5. Create agent with tools

Agent Execution:
────────────────
User: "Tell me about photovoltaic efficiency"
  ↓
Agent: "I should search the knowledge base first"
  ↓
Agent calls: knowledge_base_search("photovoltaic efficiency")
  ↓
Tool returns: [3 relevant document chunks]
  ↓
Agent: "Based on the knowledge base, PV efficiency..."
```

## Console Output Examples

### Successful Setup (First Run)

```
📄 Found 3 PDF files in knowledge base
🔄 Loading and processing documents...
  Loading: product_datasheet.pdf
  Loading: technical_specs.pdf
  Loading: installation_guide.pdf
✅ Loaded 45 pages from PDFs
✂️ Splitting documents into chunks...
✅ Created 127 text chunks
🧠 Creating embeddings and building FAISS index...
   (This may take a few minutes depending on document size)
💾 Saving FAISS index to faiss_index...
✅ Knowledge base created and saved successfully!
```

### Successful Setup (Cached)

```
📚 Loading existing FAISS index from faiss_index...
✅ Knowledge base loaded successfully!
```

### Empty Knowledge Base

```
⚠️ No PDF files found in knowledge_base/
💡 Add PDF documents to the knowledge_base/ directory to enable knowledge search.
```

### Search Results

```
Result 1:
Source: product_datasheet.pdf (Page 5)
Content: Photovoltaic modules convert sunlight directly into electricity...

---

Result 2:
Source: technical_specs.pdf (Page 12)
Content: Module efficiency ranges from 18% to 22% depending on technology...

---

Result 3:
Source: installation_guide.pdf (Page 3)
Content: Optimal installation angle for maximum efficiency is 30-35 degrees...
```

## Performance Metrics

| Operation | First Run | Cached Run |
|-----------|-----------|------------|
| Load PDFs | ~5-10s | 0s |
| Create Embeddings | ~30-60s | 0s |
| Build Index | ~5-10s | 0s |
| Load Index | 0s | ~1-2s |
| **Total** | **~40-80s** | **~1-2s** |

**Speedup: ~40x faster with caching!**

## Integration Points

1. **Agent Core**: Receives vector store during initialization
2. **Agent Tools**: Search tool registered with agent executor
3. **Agent Prompt**: Instructed to search knowledge base first
4. **UI**: Status messages displayed during setup

## Security Considerations

✅ **Path Safety**: Uses pathlib.Path for secure file operations
✅ **Input Validation**: Query strings sanitized before search
✅ **Error Isolation**: Exceptions caught and handled gracefully
✅ **No Code Execution**: Only reads PDF content, no execution
✅ **API Key Security**: OpenAI key loaded from environment

## Best Practices Implemented

1. **Caching**: Avoid redundant processing
2. **Error Handling**: Graceful degradation
3. **User Feedback**: Clear console messages
4. **Documentation**: Comprehensive docstrings
5. **Type Hints**: Full type annotations
6. **Modularity**: Separate concerns (setup vs search)
7. **Testing**: Dedicated test script
8. **Logging**: Informative progress messages

## Troubleshooting Guide

| Issue | Solution |
|-------|----------|
| No PDFs found | Add PDFs to knowledge_base/ directory |
| Embedding API error | Check OPENAI_API_KEY in .env |
| Index loading error | Delete faiss_index/ and rebuild |
| Search returns nothing | Check if PDFs contain relevant content |
| Slow startup | Ensure index is cached (check faiss_index/) |

## Next Steps

With the knowledge base system complete, the agent can now:

- ✅ Search domain-specific documents
- ✅ Retrieve relevant information
- ✅ Provide expert-level responses

Next implementation: **File System Tools** (Task 3)
