import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama, OllamaLLM
from langchain_core.messages import HumanMessage
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from vector_store import VectorStoreManager

# Load environment variables (kept for compatibility, though not needed for local Ollama)
load_dotenv()

class ChatBot:
    """
    Manages the conversational RAG pipeline using local Ollama models.
    Uses llama3.2 for fast text QA and llava:7b-q4_0 for multimodal vision QA.
    """
    
    def __init__(self, vector_store_manager: VectorStoreManager, model: str = None):
        self.vector_store_manager = vector_store_manager
        self.preferred_model = model or os.getenv("OLLAMA_TEXT_MODEL", "llama3.2")
        self.model = self.preferred_model
        self.llm = None
        self.memory = None
        self.chain = None
        
        # Initialize LLM and memory
        self._initialize_llm()
        self._initialize_memory()
            
    def _initialize_llm(self):
        """
        Initializes the local Ollama LLM for text Q&A.
        Auto-detects installed models: uses preferred model if pulled, else falls back to mistral.
        """
        try:
            active_model = self.preferred_model
            try:
                import urllib.request
                import json
                req = urllib.request.Request("http://127.0.0.1:11434/api/tags")
                with urllib.request.urlopen(req, timeout=2) as resp:
                    tags_data = json.loads(resp.read().decode())
                    available_names = [m.get("name", "").split(":")[0] for m in tags_data.get("models", [])]
                    if self.preferred_model not in available_names:
                        # Fallback order
                        for fallback in ["mistral", "gemma", "llama3.2"]:
                            if fallback in available_names:
                                print(f"Model '{self.preferred_model}' not found in Ollama yet; using available model '{fallback}'.")
                                active_model = fallback
                                break
            except Exception as check_err:
                pass
                
            self.model = active_model
            self.llm = OllamaLLM(
                model=self.model,
                temperature=0.3
            )
            print(f"Ollama text LLM initialized with model: '{self.model}'")
        except Exception as e:
            print(f"Error initializing local Ollama model: {e}")
            
    def _initialize_memory(self):
        """
        Initializes conversational memory.
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
            self._initialize_llm()
            if not self.llm:
                return False
            
        if not self.memory:
            self._initialize_memory()
            
        # Get retriever from the vector store
        retriever = self.vector_store_manager.get_retriever(k=3)
        if retriever is None:
            print("Cannot build RAG chain: Vector store is not initialized or loaded.")
            return False
            
        # Custom QA Prompt template to enforce strict context-grounding
        qa_template = """You are a strict offline document QA chatbot. 
Your ONLY source of information is the provided context. You must NOT use any outside general knowledge, assumptions, or external information. 
If the answer to the question cannot be directly and fully found in the context, you must state exactly: "I cannot find the answer in the uploaded documents." Do not attempt to guess, assume, or fabricate any answer.
Your responses must be directly grounded in the text. Your role is only to extract the relevant facts from the context and assist the user with clean sentence formation and organization of those facts.

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
        Queries the text chatbot chain with a user question.
        """
        if not self.chain:
            if not self.build_rag_chain():
                return {
                    "answer": "Chatbot is not ready. Please upload a PDF document and verify your local Ollama is running.",
                    "source_documents": []
                }
                
        try:
            response = self.chain.invoke({"question": question})
            source_documents = response.get("source_documents", [])
            
            # Fetch similarity scores directly from vector store
            docs_with_scores = []
            if self.vector_store_manager.db:
                try:
                    docs_with_scores = self.vector_store_manager.db.similarity_search_with_score(question, k=3)
                except Exception as score_err:
                    print(f"Error fetching similarity scores: {score_err}")
                    
            # Map page content to their respective L2 distance score
            score_map = {}
            for doc, score in docs_with_scores:
                score_map[doc.page_content] = score
                
            # Inject scores into metadata of the returned documents
            for doc in source_documents:
                doc.metadata["score"] = score_map.get(doc.page_content, None)

            return {
                "answer": response.get("answer", "No response generated."),
                "source_documents": source_documents
            }
        except Exception as e:
            return {
                "answer": f"Error running local model: {str(e)}. Make sure Ollama is running and you have pulled '{self.model}'.",
                "source_documents": []
            }
            
    def ask_vision(self, question: str, image_base64: str) -> dict:
        """
        Queries the local LLaVA vision model with a question and base64 image.
        Retrieves context chunks if documents are loaded to assist the model.
        """
        try:
            # Get context from retriever with similarity scores
            context_str = ""
            source_docs = []
            retriever = self.vector_store_manager.get_retriever(k=2)
            if self.vector_store_manager.db:
                try:
                    docs_with_scores = self.vector_store_manager.db.similarity_search_with_score(question, k=2)
                    for doc, score in docs_with_scores:
                        doc.metadata["score"] = score
                        source_docs.append(doc)
                    context_str = "\n\n".join([doc.page_content for doc in source_docs])
                except Exception as score_err:
                    print(f"Error fetching vision similarity scores: {score_err}")
                    if retriever is not None:
                        source_docs = retriever.invoke(question)
                        context_str = "\n\n".join([doc.page_content for doc in source_docs])
            elif retriever is not None:
                source_docs = retriever.invoke(question)
                context_str = "\n\n".join([doc.page_content for doc in source_docs])
                
            # Build prompt with document context and strict instructions
            vision_instructions = (
                "You are a strict offline vision-document QA chatbot. Your role is only to answer questions using the provided image and document context.\n"
                "Do NOT use any outside information or general knowledge. If the answer is not clearly present in the provided image or context, state exactly: 'I cannot find the answer in the uploaded documents or image.'\n"
                "Your role is strictly limited to extracting details and helping with sentence formation of those details."
            )
            if context_str:
                prompt = f"{vision_instructions}\n\nDocument Context:\n{context_str}\n\nQuestion: {question}"
            else:
                prompt = f"{vision_instructions}\n\nQuestion: {question}"
            
            # Initialize ChatOllama for vision
            vision_llm = ChatOllama(model="llava", temperature=0.3)
            
            # Format message with image using LangChain's correct multimodal syntax
            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    }
                ]
            )
            
            response = vision_llm.invoke([message])
            return {
                "answer": response.content,
                "source_documents": source_docs
            }
        except Exception as e:
            return {
                "answer": f"Error running local vision model (llava:7b-q4_0): {str(e)}. Make sure you have run 'ollama pull llava:7b-q4_0' and Ollama is running.",
                "source_documents": []
            }

    def clear_memory(self):
        """
        Resets conversational memory.
        """
        if self.memory:
            self.memory.clear()
            print("Conversational memory cleared.")
