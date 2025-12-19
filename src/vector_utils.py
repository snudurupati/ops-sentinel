import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()   # Load environment variables from .env file

KNOWLEDGE_DIR = "knowledge_base"
CHROMA_PATH = "chroma_db"

def initialize_vector_db():
    """
    Reads markdown files, chunks them, and stroes them in ChromaDB.
    Only needs to be run once or when runbooks change).
    """
    
    if not os.path.exists(KNOWLEDGE_DIR):
        print(f"Knowledge directory {KNOWLEDGE_DIR} does not exist. Please create it and add runbooks to it.")
        return None 
    
    print(f"🔄 Ingesting runbooks from {KNOWLEDGE_DIR}...")

    # 1. Load Documents
    loader = DirectoryLoader(KNOWLEDGE_DIR, glob="*.md", loader_cls=TextLoader)
    documents = loader.load()

    # 2. Split Documents (Chunking)
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)

    # 3. Create Embeddings and Store in ChromaDB
    # Note: We persist to disk so we dont have to re-ingest everytime
    vector_db = Chroma.from_documents(
        documents=docs,
        embedding=OpenAIEmbeddings(),
        persist_directory=CHROMA_PATH
    )
    print(f"✅ Indexed {len(docs)} document chunks into ChromaDB.")
    return vector_db

def get_vector_db():
    """Returns the existing ChromaDB Instance."""
    return Chroma(persist_directory=CHROMA_PATH, embedding_function=OpenAIEmbeddings())
    
def search_runbooks(query: str, k: int = 1): # <--- 1. Change default to 1
    """Searches the Vector DB for the most similar runbooks."""
    vector_db = get_vector_db()
    if not vector_db:
        print("❌ ChromaDB not initialized.")
        return ["System Error: Vector DB not ready."]
    
    # 2. Force k=1 even if the agent asks for more (Safety Cap)
    safe_k = min(k, 1)
    
    results = vector_db.similarity_search(query, k=safe_k)
    
    # 3. CRITICAL: Truncate content to 1,500 characters per result
    # This ensures one search never burns more than ~500 tokens
    clean_results = []
    for doc in results:
        content = doc.page_content
        if len(content) > 1500:
            content = content[:1500] + "... [truncated]"
        clean_results.append(content)
        
    return clean_results

# Quick test if running directly
if __name__ == "__main__":
    # Uncomment this line only for the first run to build the DB
    #initialize_vector_db() 
    
    print("\n--- Test Search (Cache Issue) ---")
    hits = search_runbooks("redis cache stampede high cpu")
    for i, hit in enumerate(hits):
        print(f"result {i+1}: {hit[:200]}...\n")
