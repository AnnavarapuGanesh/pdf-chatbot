import os
import sys
from langchain_core.documents import Document
from pdf_processor import PDFProcessor
from vector_store import VectorStoreManager
from chatbot import ChatBot

def test_pipeline():
    print("=== Step 1: Initializing Vector Store ===")
    vstore = VectorStoreManager()
    
    print("=== Step 2: Creating Mock Documents ===")
    mock_docs = [
        Document(
            page_content="Antigravity is an AI coding assistant developed by Google DeepMind. It is built to collaborate on code development and solve complex engineering tasks.",
            metadata={"source": "antigravity_intro.pdf", "page": 1}
        ),
        Document(
            page_content="The user has requested a PDF QA Chatbot using LangChain, HuggingFace embeddings, FAISS vector database, and Streamlit frontend.",
            metadata={"source": "project_spec.pdf", "page": 2}
        )
    ]
    
    print("=== Step 3: Chunking Documents ===")
    chunks = PDFProcessor.chunk_documents(mock_docs, chunk_size=100, chunk_overlap=10)
    print(f"Created {len(chunks)} chunks.")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1}: page={chunk.metadata['page']} len={len(chunk.page_content)}")
        
    print("=== Step 4: Indexing Chunks ===")
    # Clear any previous index
    vstore.clear_index()
    success = vstore.create_or_update_index(chunks)
    print(f"Indexing success: {success}")
    print(f"Used Vector Store Engine: {vstore.vector_store_type}")
    
    if not success:
        print("Failed to build index. Exiting.")
        sys.exit(1)
        
    print("=== Step 5: Loading Index ===")
    loaded = vstore.load_index()
    print(f"Index Load success: {loaded}")
    
    print("=== Step 6: Testing Retrieval ===")
    retriever = vstore.get_retriever(k=1)
    results = retriever.invoke("What is Antigravity?")
    print(f"Query Results (k=1):")
    for doc in results:
        print(f"  Source: {doc.metadata['source']} (Page {doc.metadata['page']})")
        print(f"  Content: {doc.page_content}")
        
    print("=== Step 7: Initializing ChatBot Pipeline ===")
    os.environ["GOOGLE_API_KEY"] = "MOCK_GEMINI_API_KEY_FOR_TESTING"
    bot = ChatBot(vstore)
    chain_built = bot.build_rag_chain()
    print(f"RAG Chain Build success: {chain_built}")
    
    print("=== TEST COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_pipeline()
