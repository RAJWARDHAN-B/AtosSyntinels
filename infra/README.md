# Infrastructure as Code (IaC)

Provide Bicep/Terraform modules to deploy:
- Resource Group, Storage, Key Vault, App Insights
- Azure OpenAI, Cognitive Search (vector), Document Intelligence
- Azure Functions, API Management, App Service
- Dataverse environment configuration

Include parameterized templates for environment promotion (dev/test/prod).

## Local (Zero-Cost) Infrastructure
For development without any cloud spend, use the `local/` dockerized stack instead of Azure resources:

- MinIO for object storage (replaces Blob Storage)
- Qdrant for vector search (embeddings)
- Meilisearch for keyword search
- Ollama for local LLMs
- Optional: Postgres (or SQLite) for persistence

How to run:
```
cd ../local
docker compose up -d
```

The Azure IaC remains the recommended path for production; the local stack is for demos and development only.