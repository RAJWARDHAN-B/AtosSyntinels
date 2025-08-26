# Glean - AI-Powered Legal Document Analysis Platform

A comprehensive legal document analysis platform that combines a modern React frontend with a powerful FastAPI backend powered by AI.

## 🚀 Features

- **Document Upload & Processing**: Support for PDF, TXT, CSV, XLSX, and DOCX files
- **AI-Powered Legal Analysis**: Automatic extraction of key legal information including:
  - Entities & Contact Details
  - Contract Timeline (Start/End dates)
  - Scope of Agreement
  - Service Level Agreements (SLA)
  - Penalty Clauses
  - Confidentiality Terms
  - Renewal & Termination Clauses
  - Commercial Terms
  - Risks & Assumptions
- **Interactive Chat Interface**: Ask specific questions about your documents
- **Document Summarization**: Generate comprehensive summaries
- **Modern UI/UX**: Beautiful, responsive interface with dark theme
- **Real-time Processing**: Fast AI-powered analysis using Groq LLM

## 🏗️ Architecture

```
Glean/
├── backend/                 # FastAPI Backend
│   ├── main.py             # Main API server
│   └── requirements.txt    # Python dependencies
├── glean/frontend/         # React Frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Page components
│   │   ├── context/       # React context providers
│   │   └── App.jsx        # Main app component
│   ├── package.json       # Node.js dependencies
│   └── vite.config.js     # Vite configuration
├── app.py                 # Original Streamlit app
└── requirements.txt       # Original dependencies
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Required API keys:
  - GROQ_API_KEY (for LLM processing)
  - GOOGLE_API_KEY (for embeddings)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   Create a `.env` file in the backend directory:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```

6. **Run the backend server**
   ```bash
   python main.py
   ```
   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd glean/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run the development server**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`

## 📖 Usage

1. **Upload Documents**: Use the drag-and-drop interface to upload legal documents
2. **Process Documents**: Documents are automatically processed and analyzed
3. **View Analysis**: See extracted legal information in the summary panel
4. **Chat with Documents**: Use the chatbot to ask specific questions about your documents
5. **Document History**: Access previously uploaded documents from the sidebar

## 🔧 API Endpoints

### Backend API (FastAPI)

- `POST /doc` - Upload and process a document
- `GET /doc/{doc_id}/view` - Get document content
- `POST /chat` - Get chat history for a document
- `POST /ask` - Ask a question about a document
- `POST /extract` - Extract legal information from a document
- `GET /documents` - List all uploaded documents
- `DELETE /doc/{doc_id}` - Delete a document

## 🎨 Frontend Components

- **Home**: Main dashboard with document viewer and analysis
- **Sidebar**: Document history and navigation
- **Chatbot**: Interactive AI assistant for document queries
- **ThemeProvider**: Dark/light theme management
- **PdfProvider**: Document state management

## 🔄 Integration Points

### Frontend → Backend Communication

1. **Document Upload**: Frontend sends files to `/doc` endpoint
2. **Document Analysis**: Frontend requests extraction via `/extract` endpoint
3. **Chat Interface**: Frontend sends queries to `/ask` endpoint
4. **Document History**: Frontend fetches document list via `/documents` endpoint

### AI Model Integration

- **Groq LLM**: High-performance language model for document analysis
- **Document Processing**: LangChain-based pipeline for text extraction and chunking
- **Vector Search**: FAISS-based semantic search for relevant document sections
- **Legal Extraction**: Specialized prompts for legal document analysis

## 🚀 Deployment

### Backend Deployment

The backend can be deployed to:
- **Railway**: Easy deployment with automatic scaling
- **Render**: Free tier available with automatic deployments
- **Heroku**: Traditional deployment option
- **AWS/GCP**: For enterprise deployments

### Frontend Deployment

The frontend can be deployed to:
- **Vercel**: Optimized for React applications
- **Netlify**: Easy deployment with Git integration
- **GitHub Pages**: Free static hosting
- **AWS S3**: For enterprise deployments

## 🔧 Development

### Running in Development Mode

1. **Start Backend** (Terminal 1):
   ```bash
   cd backend
   python main.py
   ```

2. **Start Frontend** (Terminal 2):
   ```bash
   cd glean/frontend
   npm run dev
   ```

3. **Access Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Environment Variables

Create `.env` files in both backend and frontend directories:

**Backend (.env)**:
```
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

**Frontend (.env)**:
```
VITE_BACKEND_URL=http://localhost:8000
```

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure the backend CORS settings include your frontend URL
2. **API Key Issues**: Verify your GROQ_API_KEY and GOOGLE_API_KEY are set correctly
3. **Port Conflicts**: Make sure ports 3000 (frontend) and 8000 (backend) are available
4. **Dependency Issues**: Run `npm install` and `pip install -r requirements.txt`

### Debug Mode

Enable debug logging by setting environment variables:
```
DEBUG=true
LOG_LEVEL=DEBUG
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the Atos Srijan Hackathon submission.

---

**Made with ❤ by Glean Team**
