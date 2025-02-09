import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pypdf import PdfReader

# Load environment variables
load_dotenv()

# Initialize Groq LLM
llm = Groq(
    model="mixtral-8x7b-32768",
    api_key=os.getenv("GROQ_API_KEY")
)

# Set up embeddings
embeddings = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Configure global settings to use Groq
Settings.llm = llm
Settings.embed_model = embeddings

def load_pdf_content(file_path):
    """Load content from a PDF file."""
    pdf_reader = PdfReader(file_path)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def load_and_index_pdf(pdf_directory: str):
    """Load PDF files from directory and create an index."""
    documents = []
    
    # Read all PDF files in the directory
    for file in os.listdir(pdf_directory):
        if file.endswith('.pdf'):
            file_path = os.path.join(pdf_directory, file)
            content = load_pdf_content(file_path)
            doc = Document(text=content)
            documents.append(doc)
    
    # Create index from documents - no need to pass llm and embed_model here as they're set globally
    index = VectorStoreIndex.from_documents(documents)
    return index

def create_chat_engine(index):
    """Create a chat engine from the index."""
    return index.as_chat_engine(
        chat_mode="condense_plus_context",
        verbose=True
    )

def main():
    # Directory containing your PDF files
    pdf_dir = "pdfs"
    
    try:
        # Create index from PDF files
        print("Loading and indexing PDF files...")
        index = load_and_index_pdf(pdf_dir)
        
        # Create chat engine
        chat_engine = create_chat_engine(index)
        
        print("\nChat initialized! Type 'exit' to end the conversation.")
        
        # Start chat loop
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            # Get response from chat engine
            response = chat_engine.chat(user_input)
            print(f"\nAssistant: {response}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
