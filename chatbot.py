import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from vector_store import VectorStoreManager

# Load environment variables at module initialization
load_dotenv()

class ChatBot:
    """
    Manages the conversational RAG pipeline using Google Gemini models,
    LangChain orchestration, and conversation history memory.
    """
    
    def __init__(self, vector_store_manager: VectorStoreManager, model: str = "gemini-2.5-flash"):
        self.vector_store_manager = vector_store_manager
        self.model = model
        self.llm = None
        self.memory = None
        self.chain = None
        
        # Verify API key exists
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if self.api_key:
            self._initialize_llm()
            self._initialize_memory()
            
    def _initialize_llm(self):
        """
        Initializes the Google Gemini Chat LLM.
        """
        self.llm = ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.api_key,
            temperature=0.0,  # Lower temperature = more deterministic, factual answers
            max_output_tokens=1024
        )
        
    def _initialize_memory(self):
        """
        Initializes conversational memory.
        Uses ConversationBufferWindowMemory to retain context of recent turns.
        """
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            output_key="answer",
            return_messages=True,
            k=5  # Remember last 5 dialogue turns
        )
        
    def build_rag_chain(self) -> bool:
        """
        Constructs the conversational retrieval chain.
        """
        if not self.llm:
            # Try initializing again if environment variables changed
            self.api_key = os.environ.get("GOOGLE_API_KEY")
            if not self.api_key:
                print("Cannot build RAG chain: GOOGLE_API_KEY is missing.")
                return False
            self._initialize_llm()
            
        if not self.memory:
            self._initialize_memory()
            
        # Get retriever from the vector store
        retriever = self.vector_store_manager.get_retriever(k=3)
        if retriever is None:
            print("Cannot build RAG chain: Vector store is not initialized or loaded.")
            return False
            
        # Custom QA Prompt template to enforce strict context-grounding
        qa_template = """You are an advanced document QA chatbot. Use the following pieces of context to answer the user's question. 
If you do not know the answer based on the provided context, state clearly that you cannot find the answer in the uploaded documents. Do not try to make up or hallucinate an answer.
Keep your answer detailed but concise and directly grounded in the context.

Context:
{context}

Question: {question}
Helpful Answer:"""
        
        QA_PROMPT = PromptTemplate(
            template=qa_template, 
            input_variables=["context", "question"]
        )
        
        # Build the conversational chain
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": QA_PROMPT},
            output_key="answer"
        )
        return True

    def ask(self, question: str) -> dict:
        """
        Queries the chatbot chain with a user question.
        
        Args:
            question (str): User question.
            
        Returns:
            dict: Dictionary containing 'answer' and 'source_documents'.
        """
        if not self.chain:
            # Try to build the chain dynamically
            if not self.build_rag_chain():
                return {
                    "answer": "Chatbot is not ready. Please upload a PDF document and verify your GOOGLE_API_KEY in the `.env` file first.",
                    "source_documents": []
                }
                
        try:
            # Get response from chain
            response = self.chain.invoke({"question": question})
            return {
                "answer": response.get("answer", "No response generated."),
                "source_documents": response.get("source_documents", [])
            }
        except Exception as e:
            return {
                "answer": f"An error occurred while processing your request: {str(e)}",
                "source_documents": []
            }
            
    def clear_memory(self):
        """
        Resets conversational memory.
        """
        if self.memory:
            self.memory.clear()
            print("Conversational memory cleared.")
