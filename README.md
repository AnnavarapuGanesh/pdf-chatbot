# PDF QA Chatbot v2.0 (Offline & Multimodal)

An interactive, **100% offline, privacy-first** RAG application that allows users to upload PDF documents and ask questions about their content in natural language. Additionally supports a **multimodal image analysis feature** allowing users to attach images and examine them with the local model.

Upgraded to **Version 2.0**: Shunted from Streamlit/Gemini to a decoupled **React (Vite) + FastAPI + Ollama** architecture.

---

## Architecture
- **Frontend**: React 18 + Vite (Premium Dark Glassmorphic UI)
- **Backend Server**: FastAPI REST API (Uvicorn)
- **Local LLM Engine**: Ollama
  - **Text Q&A Model**: `llama3.2` (3B, ~2GB)
  - **Vision Q&A Model**: `llava` (Quantized 7B multimodal, ~4.7GB)
- **Vector Database**: FAISS (Fallback to ChromaDB)
- **Embeddings**: HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`)
- **PDF Processing**: PyMuPDF (`fitz`)

---

## Prerequisites (One-time Setup)

1. **Install Ollama**: Download and run the installer from [ollama.com](https://ollama.com).
2. **Pull the Models**: Open a terminal and download the required local models:
   ```bash
   ollama pull llama3.2
   ollama pull llava
   ```
   *Note: Ollama runs as a background Windows service automatically.*

---

## Installation & Startup

Clone the repository and follow the instructions to run the two servers.

### 1. Backend Setup (FastAPI)
Open a terminal in the root project folder:
```powershell
# Navigate to the backend directory
cd backend

# Start the FastAPI server (port 8000) using the parent virtual environment
..\venv\Scripts\python -m uvicorn main:app --reload --port 8000
```
*The API Swagger docs will be live at `http://localhost:8000/docs`.*

---

### 2. Frontend Setup (React)
Open a second terminal in the `frontend/` folder:
```bash
# Navigate and install node packages
cd frontend
npm install

# Start Vite dev server (port 5173)
npm run dev
```
*Open your browser and navigate to `http://localhost:5173` to use the application.*

---

## Key Features & UI Behaviours
*   **Dual Mode Indicator**: The input field displays a badge showing **"Text Mode (Llama 3.2)"** by default. Once an image is attached, the badge dynamically shifts to **"Vision Mode (LLaVA)"**.
*   **Image Compression**: Attached images are automatically resized to a maximum of **1024px** on the longest side using an HTML5 canvas element before being converted to base64. This speeds up LLaVA CPU inference and keeps network payloads small.
*   **Stateless Image Analysis**: To conserve memory and CPU execution times, image-based Q&A is processed statelessly (past dialogue histories are not passed to LLaVA), whereas text-only queries preserve conversational memory history.
*   **Citations Drawer**: Clicking **"View Sources"** below any bot response slides open a glassmorphic drawer containing the exact reference text snippets and page numbers from the indexed documents.
*   **Light & Dark Theme Toggle**: Easily switch between a premium dark glassmorphic design and a clean, high-contrast light mode using the Sun/Moon icon in the top header.
*   **Strict Context Grounding**: Instructs both the text (`llama3.2`) and vision (`llava`) models to restrict responses to the uploaded documents and image, preventing hallucinations and general-knowledge leaks.
