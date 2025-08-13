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
