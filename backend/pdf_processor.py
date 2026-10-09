import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os
import io

# Tesseract OCR setup
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
    # Auto-detect Tesseract executable on Windows
    for t_path in [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]:
        if os.path.exists(t_path):
            pytesseract.pytesseract.tesseract_cmd = t_path
            break
except ImportError:
    TESSERACT_AVAILABLE = False

class PDFProcessor:
    """
    Handles extracting text from PDF files page-by-page and splitting it into manageable chunks.
    Preserves page number and source file metadata for citation.
    Includes OCR fallback for scanned documents.
    """
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str, original_filename: str = None) -> list[Document]:
        """
        Extracts text from a PDF file page by page.
        
        Args:
            pdf_path (str): Absolute or relative path to the PDF file.
            original_filename (str): Optional actual uploaded filename for citation metadata.
            
        Returns:
            list[Document]: A list of LangChain Document objects, one per page.
        """
        documents = []
        pdf_name = original_filename if original_filename else os.path.basename(pdf_path)
        
        try:
            # Open PDF using PyMuPDF
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                # If page has no native text, attempt OCR fallback
                if not text.strip() and TESSERACT_AVAILABLE:
                    try:
                        pix = page.get_pixmap(dpi=150)
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        ocr_text = pytesseract.image_to_string(img)
                        if ocr_text.strip():
                            text = ocr_text
                    except Exception as ocr_err:
                        print(f"OCR note for page {page_num + 1} of {pdf_name}: {ocr_err}")
                
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
