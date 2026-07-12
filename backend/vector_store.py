import os
import shutil
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

class VectorStoreManager:
    """
    Manages vector embeddings and indexing using sentence-transformers and FAISS.
    Includes a fallback mechanism to Chroma if FAISS installation or loading fails on Windows.
    """
    
    def __init__(self, persist_dir: str = "faiss_index"):
        # We target faiss_index or chroma_db inside the persist_dir folder
        self.persist_dir = persist_dir
        # Initialize HuggingFace embeddings (all-MiniLM-L6-v2 yields 384-dimensional vectors)
        print("Initializing HuggingFace embedding model (all-MiniLM-L6-v2)...")
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store_type = None
        self.db = None
        
    def create_or_update_index(self, documents: list[Document], append: bool = False) -> bool:
        """
        Creates or updates the vector store with new documents.
        Tries FAISS first, then falls back to Chroma.
        
        Args:
            documents (list[Document]): List of documents to embed and index.
            append (bool): If True, appends to existing index; otherwise overwrites.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not documents:
            return False
            
        # Try FAISS first
        try:
            from langchain_community.vectorstores import FAISS
            print("Attempting to use FAISS vector store...")
            
            # Check if index already exists and we want to append
            if append and os.path.exists(self.persist_dir) and os.path.exists(os.path.join(self.persist_dir, "index.faiss")):
                print("Loading existing FAISS index to append documents...")
                db = FAISS.load_local(self.persist_dir, self.embeddings, allow_dangerous_deserialization=True)
                db.add_documents(documents)
            else:
                print("Creating new FAISS index (overwriting)...")
                db = FAISS.from_documents(documents, self.embeddings)
            
            os.makedirs(self.persist_dir, exist_ok=True)
            db.save_local(self.persist_dir)
            self.db = db
            self.vector_store_type = "FAISS"
            print("FAISS index saved successfully.")
            return True
            
        except Exception as faiss_err:
            print(f"FAISS failed or not installed: {faiss_err}. Falling back to Chroma...")
            
            # Fallback to Chroma
            try:
                from langchain_community.vectorstores import Chroma
                chroma_dir = "chroma_db"
                
                # If we are overwriting and folder exists, try to clear it first
                if not append and os.path.exists(chroma_dir):
                    try:
                        shutil.rmtree(chroma_dir)
                    except Exception as e:
                        print(f"Chroma clear warning: {e}")
                
                print("Creating/loading Chroma database...")
                db = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory=chroma_dir
                )
                self.db = db
                self.vector_store_type = "Chroma"
                print("Chroma database saved successfully.")
                return True
            except Exception as chroma_err:
                print(f"Chroma fallback failed as well: {chroma_err}")
                return False

    def load_index(self) -> bool:
        """
        Loads the vector store from local storage.
        Checks FAISS first, then Chroma.
        
        Returns:
            bool: True if index loaded successfully.
        """
        # Try FAISS
        if os.path.exists(self.persist_dir) and os.path.exists(os.path.join(self.persist_dir, "index.faiss")):
            try:
                from langchain_community.vectorstores import FAISS
                self.db = FAISS.load_local(self.persist_dir, self.embeddings, allow_dangerous_deserialization=True)
                self.vector_store_type = "FAISS"
                print("FAISS index loaded successfully.")
                return True
            except Exception as e:
                print(f"Error loading FAISS index: {e}. Trying Chroma...")
                
        # Try Chroma
        chroma_dir = "chroma_db"
        if os.path.exists(chroma_dir):
            try:
                from langchain_community.vectorstores import Chroma
                self.db = Chroma(persist_directory=chroma_dir, embedding_function=self.embeddings)
                self.vector_store_type = "Chroma"
                print("Chroma database loaded successfully.")
                return True
            except Exception as e:
                print(f"Error loading Chroma database: {e}")
                
        return False

    def get_retriever(self, k: int = 3):
        """
        Returns a retriever object for similarity searches.
        """
        if self.db is None:
            if not self.load_index():
                return None
        
        return self.db.as_retriever(search_kwargs={"k": k})
        
    def clear_index(self):
        """
        Removes the persistent vector databases.
        """
        self.db = None
        self.vector_store_type = None
        
        # Try to delete folders, but handle lock errors on Windows gracefully
        for folder in [self.persist_dir, "chroma_db"]:
            if os.path.exists(folder):
                try:
                    shutil.rmtree(folder)
                except Exception as e:
                    print(f"Windows file lock warning: Could not delete {folder} directory: {e}")
        print("Vector database directories cleared.")
