import os
import uuid
import time
from typing import List, Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import Document

from pypdf import PdfReader


# -----------------------------------------------------------------------------
# Environment and setup
# -----------------------------------------------------------------------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Glean Backend", version="1.0.0")

# CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# In-memory store (simple dev implementation)
# -----------------------------------------------------------------------------
class StoredDocument(BaseModel):
    document_id: str
    original_filename: str
    file_path: str
    text_chunks: List[str]
    chat: List[Dict[str, Any]]


DOCUMENTS: Dict[str, StoredDocument] = {}


# -----------------------------------------------------------------------------
# LLM and prompts
# -----------------------------------------------------------------------------
llm = None
if GROQ_API_KEY:
    llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="Llama3-8b-8192")

qa_prompt = ChatPromptTemplate.from_template(
    """
You are a legal document assistant. Provide precise and contextual answers.

Document Context:
<context>
{context}
</context>

User Question: {input}

Provide a clear, concise answer based strictly on the document context.
"""
)


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------
def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    texts: List[str] = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)


def split_into_chunks(text: str) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    documents = splitter.create_documents([text])
    return [d.page_content for d in documents]


def simple_text_search(query: str, documents_text: List[str], top_k: int = 5) -> List[str]:
    query_lower = (query or "").lower()
    if not query_lower or not documents_text:
        return documents_text[:top_k]

    scored: List[Any] = []
    for idx, doc_text in enumerate(documents_text):
        lower = doc_text.lower()
        score = sum(1 for word in query_lower.split() if word in lower)
        if score > 0:
            scored.append((score, doc_text, idx))

    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        return documents_text[:top_k]
    return [doc_text for score, doc_text, idx in scored[:top_k]]


# -----------------------------------------------------------------------------
# Schemas
# -----------------------------------------------------------------------------
class AskRequest(BaseModel):
    doc_id: str
    query: str


class ChatRequest(BaseModel):
    doc_id: str


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@app.post("/doc")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    document_id = uuid.uuid4().hex
    dest_path = os.path.join(UPLOAD_DIR, f"{document_id}.pdf")

    content = await file.read()
    with open(dest_path, "wb") as f:
        f.write(content)

    try:
        text = extract_text_from_pdf(dest_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read PDF: {e}")

    chunks = split_into_chunks(text)

    DOCUMENTS[document_id] = StoredDocument(
        document_id=document_id,
        original_filename=file.filename,
        file_path=dest_path,
        text_chunks=chunks,
        chat=[],
    )

    return {"document_id": document_id}


@app.get("/doc/{doc_id}/view")
async def view_document(doc_id: str):
    doc = DOCUMENTS.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return FileResponse(path=doc.file_path, filename=doc.original_filename, media_type="application/pdf")


@app.post("/ask")
async def ask_document(request: AskRequest):
    doc = DOCUMENTS.get(request.doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    relevant = simple_text_search(request.query, doc.text_chunks)
    documents = [Document(page_content=t) for t in relevant]

    if llm is None:
        answer = "LLM not configured. Please set GROQ_API_KEY. Showing first relevant chunk:\n\n" + (relevant[0] if relevant else "No content available")
    else:
        chain = create_stuff_documents_chain(llm, qa_prompt)
        start = time.process_time()
        response = chain.invoke({"context": documents, "input": request.query})
        _elapsed = time.process_time() - start
        answer = response.get("answer") if isinstance(response, dict) else str(response)

    doc.chat.append({"query": request.query, "answer": answer})

    return {"answer": answer}


@app.post("/chat")
async def chat_history(request: ChatRequest):
    doc = DOCUMENTS.get(request.doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"chat": doc.chat}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


