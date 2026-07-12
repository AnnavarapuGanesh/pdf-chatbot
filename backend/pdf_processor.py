import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os

class PDFProcessor:
    """
    Handles extracting text from PDF files page-by-page and splitting it into manageable chunks.
    Preserves page number and source file metadata for citation.
    """
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> list[Document]:
        """
        Extracts text from a PDF file page by page.
        
        Args:
            pdf_path (str): Absolute or relative path to the PDF file.
            
        Returns:
            list[Document]: A list of LangChain Document objects, one per page.
        """
        documents = []
        pdf_name = os.path.basename(pdf_path)
        
        try:
            # Open PDF using PyMuPDF
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    metadata = {
                        "source": pdf_name,
                        "page": page_num + 1  # 1-indexed page number
                    }
                    documents.append(Document(page_content=text, metadata=metadata))
            doc.close()
        except Exception as e:
            print(f"Error reading PDF {pdf_name}: {e}")
            
        return documents

    @staticmethod
    def chunk_documents(documents: list[Document], chunk_size: int = 1000, chunk_overlap: int = 100) -> list[Document]:
        """
        Chunks text documents into smaller chunks while preserving metadata.
        
        Args:
            documents (list[Document]): List of documents to split.
            chunk_size (int): Max size of each chunk (characters).
            chunk_overlap (int): Overlap between chunks (characters).
            
        Returns:
            list[Document]: List of chunked documents.
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        return text_splitter.split_documents(documents)
