import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

load_dotenv()
# print("KEY:", repr(os.getenv("GEMINI_API_KEY")))

class RAGService :
    _cached_vector_store = None

    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            api_key=os.getenv("GEMINI_API_KEY")
        )
        
        if RAGService._cached_vector_store is None:
            print("Building in-memory vector store cache...")
            vector_store = InMemoryVectorStore(self.embeddings)
            
            # Resolve absolute path to Assets/my_resume.pdf
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            file_path = os.path.join(base_dir, "Assets", "my_resume.pdf")
            
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=128)
            chunks = splitter.split_documents(pages)
            vector_store.add_documents(chunks)
            RAGService._cached_vector_store = vector_store
            print("In-memory vector store cache built successfully!")
            
        self.vector_store = RAGService._cached_vector_store
        
    def process_and_create_embeddings(self, file_path: str = None):
        # Maintained for backward compatibility
        pass
        
    def get_retriever(self):
        retriever=self.vector_store.as_retriever(search_kwargs={"k": 2})
        return retriever
    
if __name__ == "__main__":
    rag_service =RAGService()
    print("-------------VECTORE DB IS READY----------------")
    retriever = rag_service.get_retriever()
    docs = retriever.invoke("What is your name?")
    print(docs)
