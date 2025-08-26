from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import tempfile
import time
import json
from typing import List, Optional
from pydantic import BaseModel
import uvicorn

# Import the ML model functionality from the existing app
import sys
sys.path.append('../')

# Import the document processing functions from the Streamlit app
import os
import tempfile
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    TextLoader,
    CSVLoader,
    UnstructuredExcelLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.schema import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize LLM
groq_api_key = os.getenv('GROQ_API_KEY')
llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")

# Prompts
LEGAL_EXTRACTION_PROMPT = """You are an expert legal document analyst. Your task is to extract and categorize key details from the given legal document, ensuring accuracy and completeness. 
Even if the exact term is not mentioned, identify similar phrases or concepts that convey the same meaning. If no relevant information is found, explicitly state "N/A".

### 🔍 Extraction Guidelines:

#### 1️⃣ Entities & Contact Details
   - Identify all parties involved (individuals, companies, organizations).
   - Extract full legal names.
   - Capture addresses, emails, and phone numbers.

#### 2️⃣ Contract Start Date & End Date
   - Locate the contract's effective date (start date).
   - Identify the expiration or termination date.
   - Note any key milestone dates (e.g., renewal deadlines, review periods).

#### 3️⃣ Scope of Agreement
   - Clearly define the document's purpose.
   - Highlight key obligations, deliverables, and services mentioned.
   - Extract any relevant exclusions or limitations.

#### 4️⃣ Service Level Agreement (SLA)
   - Extract performance metrics, response times, and service standards.
   - Identify any penalties for SLA breaches.

#### 5️⃣ Penalty Clauses
   - Identify conditions that trigger penalties.
   - Extract monetary/legal consequences for non-compliance.
   - Define what constitutes a breach or violation.

#### 6️⃣ Confidentiality Clause
   - Identify confidentiality obligations and restrictions.
   - Extract the duration and scope of confidentiality terms.

#### 7️⃣ Renewal & Termination Clause
   - Extract conditions for renewal (auto-renewal, renegotiation terms).
   - Identify termination clauses (grounds for termination).
   - Note any required notice periods.

#### 8️⃣ Commercials / Payment Terms
   - Extract payment terms, pricing structures, and invoicing details.
   - Identify due dates, penalties for late payments, and refund policies.

#### 9️⃣ Risks & Assumptions
   - Identify potential risks associated with the agreement.
   - Extract any stated mitigation strategies or underlying assumptions.

If any section is missing, explicitly return "N/A".

---

### 📜 Document Context:
<context>
{context}
</context>

### 🔍 Extraction Task:
Extract and categorize all legal information following the above structure. If specific terms are not found, look for synonyms or related phrases. If no relevant information exists, return "N/A".
"""

extraction_prompt = ChatPromptTemplate.from_template(
    f"""
{LEGAL_EXTRACTION_PROMPT}

📜 *Document Context*:
<context>
{{context}}
</context>

🔍 *Extraction Task*: Extract and categorize all available legal information from the document.
"""
)

qa_prompt = ChatPromptTemplate.from_template(
    f"""
You are a legal document assistant. Provide precise and contextual answers.

📜 *Document Context*:
<context>
{{context}}
</context>

🔍 *User Question*: {{input}}

Provide a clear, concise answer based strictly on the document context.
"""
)

# Document processing functions
def process_uploaded_file(uploaded_file):
    file_name = uploaded_file.filename
    file_extension = file_name.split('.')[-1].lower()

    # Create a temporary file to store the uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
        tmp_file.write(uploaded_file.file.read())
        tmp_path = tmp_file.name

    # Process different file types
    try:
        if file_extension == 'pdf':
            loader = PyPDFLoader(tmp_path)
            documents = loader.load()
        elif file_extension == 'txt':
            loader = TextLoader(tmp_path)
            documents = loader.load()
        elif file_extension == 'csv':
            loader = CSVLoader(tmp_path)
            documents = loader.load()
        elif file_extension == 'xlsx':
            loader = UnstructuredExcelLoader(tmp_path)
            documents = loader.load()
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    finally:
        # Clean up the temporary file
        os.unlink(tmp_path)

    return documents

def vector_embedding(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    final_documents = text_splitter.split_documents(documents)
    return final_documents

def simple_text_search(query, documents_text, top_k=5):
    """Simple text-based search using keyword matching"""
    query_lower = query.lower()
    results = []
    
    # If no query or empty documents, return all documents
    if not query or not documents_text:
        return documents_text[:top_k]
    
    for i, doc_text in enumerate(documents_text):
        doc_lower = doc_text.lower()
        # Simple keyword matching
        score = sum(1 for word in query_lower.split() if word in doc_lower)
        if score > 0:
            results.append((score, doc_text, i))
    
    # Sort by score and return top_k results
    results.sort(key=lambda x: x[0], reverse=True)
    
    # If no matches found, return first few documents
    if not results:
        return documents_text[:top_k]
    
    return [doc_text for score, doc_text, idx in results[:top_k]]

def convert_to_json(extraction_text):
    """Convert the extracted text into a structured JSON format"""
    sections = {
        "entities_and_contacts": {},
        "contract_timeline": {},
        "scope": "",
        "sla_clauses": [],
        "penalty_clauses": [],
        "confidentiality": {},
        "renewal_termination": {},
        "commercial_terms": {},
        "risks_assumptions": []
    }
    
    # Parse the extraction text and populate sections
    current_section = None
    for line in extraction_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if any(key.replace('_', ' ').upper() in line.upper() for key in sections.keys()):
            current_section = next(key for key in sections.keys() if key.replace('_', ' ').upper() in line.upper())
            continue
            
        if current_section and line:
            if isinstance(sections[current_section], dict):
                # Split on first colon for key-value pairs
                if ':' in line:
                    key, value = line.split(':', 1)
                    sections[current_section][key.strip()] = value.strip()
            elif isinstance(sections[current_section], list):
                sections[current_section].append(line)
            else:
                sections[current_section] = line
    
    return sections

def estimate_tokens(text):
    """Rough estimate of token count (1 token ≈ 4 characters)"""
    return len(text) // 4

app = FastAPI(title="Glean API", description="AI-powered legal document analysis")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://glean-frontend.onrender.com",
        "https://glean.onrender.com"
    ],  # React dev server and Render domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for documents (in production, use a database)
documents_store = {}
chat_history = {}

class ChatRequest(BaseModel):
    doc_id: str
    query: str

class DocumentResponse(BaseModel):
    document_id: str
    message: str

@app.post("/doc", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a legal document"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.txt', '.csv', '.xlsx')):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Read file content
        content = await file.read()
        
        # Create a mock uploaded file object for processing
        class MockUploadedFile:
            def __init__(self, filename, content):
                self.filename = filename
                self.content = content
                self.file = type('MockFile', (), {'read': lambda: content})()
        
        mock_file = MockUploadedFile(file.filename, content)
        
        # Process the document using the existing ML pipeline
        documents = process_uploaded_file(mock_file)
        if not documents:
            raise HTTPException(status_code=400, detail="Failed to process document")
        
        # Create vector embeddings
        final_documents = vector_embedding(documents)
        
        # Generate a unique document ID
        doc_id = f"doc_{int(time.time())}_{hash(file.filename)}"
        
        # Store document data
        documents_store[doc_id] = {
            "filename": file.filename,
            "documents_text": [doc.page_content for doc in final_documents],
            "documents_metadata": [doc.metadata for doc in final_documents],
            "processed_files": [file.filename]
        }
        
        # Initialize chat history for this document
        chat_history[doc_id] = []
        
        return DocumentResponse(
            document_id=doc_id,
            message="Document uploaded and processed successfully"
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/doc/{doc_id}/view")
async def view_document(doc_id: str):
    """Get document content for viewing"""
    if doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_data = documents_store[doc_id]
    return {
        "filename": doc_data["filename"],
        "content": doc_data["documents_text"][:5],  # Return first 5 chunks for preview
        "total_chunks": len(doc_data["documents_text"])
    }

@app.post("/chat")
async def get_chat_history(request: ChatRequest):
    """Get chat history for a document"""
    doc_id = request.doc_id
    if doc_id not in chat_history:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"chat": chat_history[doc_id]}

@app.post("/ask")
async def ask_question(request: ChatRequest):
    """Ask a question about a document"""
    doc_id = request.doc_id
    query = request.query
    
    if doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        doc_data = documents_store[doc_id]
        
        # Use simple text search to get relevant documents
        relevant_docs = simple_text_search(query, doc_data["documents_text"])
        
        # Create documents for the chain
        documents = [Document(page_content=doc) for doc in relevant_docs]
        
        # Create the document chain
        document_chain = create_stuff_documents_chain(llm, qa_prompt)
        
        # Get the answer
        start = time.process_time()
        response = document_chain.invoke({'context': documents, 'input': query})
        elapsed = time.process_time() - start
        
        # Handle response
        if isinstance(response, dict):
            answer = response.get('answer', str(response))
        else:
            answer = str(response)
        
        # Store in chat history
        chat_history[doc_id].append({
            "query": query,
            "answer": answer,
            "timestamp": time.time()
        })
        
        return {
            "answer": answer,
            "processing_time": elapsed,
            "relevant_chunks": len(documents)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")

@app.post("/extract")
async def extract_legal_info(doc_id: str = Form(...)):
    """Extract legal information from a document"""
    if doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        doc_data = documents_store[doc_id]
        all_docs = doc_data["documents_text"]
        
        # Limit documents to avoid token limit issues
        max_chunks = min(2, len(all_docs))
        selected_docs = all_docs[:max_chunks]
        
        # Create documents for the chain
        documents = [Document(page_content=doc) for doc in selected_docs]
        
        # Create extraction chain
        document_chain = create_stuff_documents_chain(llm, extraction_prompt)
        
        # Extract information
        start = time.process_time()
        response = document_chain.invoke({'context': documents, 'input': 'Extract all key legal information from the document'})
        elapsed = time.process_time() - start
        
        # Handle response
        if isinstance(response, dict):
            answer = response.get('answer', str(response))
        else:
            answer = str(response)
        
        # Convert to JSON
        json_data = convert_to_json(answer)
        
        return {
            "extraction": answer,
            "json_data": json_data,
            "processing_time": elapsed,
            "chunks_processed": len(documents)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract information: {str(e)}")

@app.get("/documents")
async def list_documents():
    """List all uploaded documents"""
    return {
        "documents": [
            {
                "id": doc_id,
                "name": data["filename"],
                "chunks": len(data["documents_text"])
            }
            for doc_id, data in documents_store.items()
        ]
    }

@app.delete("/doc/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document"""
    if doc_id not in documents_store:
        raise HTTPException(status_code=404, detail="Document not found")
    
    del documents_store[doc_id]
    if doc_id in chat_history:
        del chat_history[doc_id]
    
    return {"message": "Document deleted successfully"}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
