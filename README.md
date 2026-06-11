# PDF QA Chatbot

An AI-powered chatbot that allows users to upload PDF documents and ask questions about their content in natural language. Powered by **Google Gemini 1.5 Flash**, **LangChain**, and **FAISS** (with automatic fallback to **Chroma**). Deployed on Streamlit.

---

## Features
- **PDF Upload**: Drag-and-drop or browse multiple PDF files.
- **Context-Grounded Q&A**: Answers are generated strictly based on document content (zero hallucinations).
- **Source Citations**: Displays exact source text and page numbers for transparency.
- **Conversational Memory**: Retains the context of the conversation for follow-up questions.
- **Premium Glassmorphic UI**: Sleek, modern, dark-themed user interface.
- **Chroma Fallback**: Built-in compatibility layer to switch vector databases if FAISS fails on your platform.

---

## Tech Stack
- **Web UI**: Streamlit
- **LLM Engine**: Google Gemini 2.5 Flash
- **Orchestration**: LangChain
- **Embeddings**: HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`)
- **Vector Database**: FAISS (Fallback to ChromaDB)
- **PDF Extraction**: PyMuPDF (`fitz`)

---

## Local Setup Instructions

### 1. Clone & Navigate
```bash
git clone https://github.com/<your-username>/pdf-chatbot.git
cd pdf-chatbot
```

### 2. Set Up Virtual Environment
On Windows (PowerShell):
```powershell
python -m venv venv
venv\Scripts\activate
```
On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
> **Note for Windows users**: If FAISS fails to install due to C++ compilation environments, run:
> ```bash
> pip install faiss-cpu --no-cache-dir
> ```
> If it still fails, the application will automatically use **ChromaDB** instead.

### 4. Setup API Key
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```
> Get a free API Key from [Google AI Studio](https://aistudio.google.com).

### 5. Run the Application
```bash
streamlit run app.py
```

---

## Streamlit Cloud Deployment

Streamlit Cloud allows you to host this app for free directly from your GitHub repository.

### Steps:
1. Push your project to a public **GitHub** repository. Ensure `.env` and `faiss_index/` / `chroma_db/` are **not** committed (they should be listed in your `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
3. Click **"New App"**.
4. Select your Repository, Branch (usually `main`), and set the Main File path to `app.py`.
5. Open **"Advanced Settings"** before deploying.
6. Under **Secrets**, define your Google API key:
   ```toml
   GOOGLE_API_KEY = "your_actual_gemini_api_key"
   ```
7. Click **"Deploy"**. Your application will be live at a custom sub-domain in a few minutes!
