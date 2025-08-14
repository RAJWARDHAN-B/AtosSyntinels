# Azure Functions (Orchestrator)

This folder will contain the Functions app for orchestration:
- Ingestion trigger (Event Grid) on Blob upload
- Document Intelligence call
- Cognitive Search indexing and embeddings
- RAG prompts for clause extraction, summary, and risk
- Persistence to Dataverse/Cosmos and status updates

Suggested structure:
- /src/OrchestratorFunction
- /src/IndexingFunction
- /src/RagFunction
- /tests

## Local Orchestrator (Zero-Cost Alternative)
If you cannot use Azure Functions, implement a local orchestrator service (e.g., FastAPI/Node) that targets the `local/` stack:

- OCR: Tesseract via `pytesseract` or PaddleOCR
- Parsing: PyMuPDF / pdfminer.six
- Embeddings: `sentence-transformers` with a local model (e.g., `all-MiniLM-L6-v2` via `onnx`/`cpu`)
- Vector DB: Qdrant via `qdrant-client`
- Search: Meilisearch client
- LLM: Ollama HTTP API
- Storage: MinIO S3 SDK
- DB: SQLite/Postgres (local)

Use `MODE=local` to switch dependencies and endpoints at runtime.