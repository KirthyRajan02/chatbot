import os
import json
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from pypdf import PdfReader

# Load environment variables
load_dotenv()

class DataTools:
    def __init__(self):
        # Initialize Groq LLM
        self.llm = Groq(
            model="mixtral-8x7b-32768",
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        # Set up embeddings
        self.embeddings = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        
        # Configure global settings
        Settings.llm = self.llm
        Settings.embed_model = self.embeddings
        
        # Initialize storage for different data sources
        self.pdf_index = None
        self.api_index = None
        self.api_data = None

    def load_pdf_content(self, file_path: str) -> str:
        """Load content from a PDF file."""
        pdf_reader = PdfReader(file_path)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    def initialize_pdf_index(self, pdf_directory: str) -> None:
        """Initialize the PDF index from a directory of PDF files."""
        documents = []
        
        for file in os.listdir(pdf_directory):
            if file.endswith('.pdf'):
                file_path = os.path.join(pdf_directory, file)
                content = self.load_pdf_content(file_path)
                doc = Document(text=content)
                documents.append(doc)
        
        self.pdf_index = VectorStoreIndex.from_documents(documents)

    def fetch_api_data(self, api_url: str) -> Dict[str, Any]:
        """Fetch data from the specified API endpoint."""
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            self.api_data = response.json()
            return self.api_data
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch API data: {str(e)}")

    def initialize_api_index(self, api_url: str) -> None:
        """Initialize the API data index with structured tourism information."""
        if not self.api_data:
            self.fetch_api_data(api_url)
        
        # Create structured documents for different aspects of the data
        documents = []
        
        # Metrics document
        metrics_text = f"""
        Tourism Overview Metrics:
        - Total Trainees: {self.api_data['metrics']['totalTrainees']}
        - Total Cities: {self.api_data['metrics']['totalCities']}
        - Total Entities: {self.api_data['metrics']['totalEntities']}
        - Total Students: {self.api_data['metrics']['totalStudents']}
        """
        documents.append(Document(text=metrics_text))
        
        # Top Entities document
        entities_text = "Top Tourism Entities:\n"
        for entity in self.api_data['topEntities']:
            entities_text += f"""
            Entity: {entity['entityName']}
            - Number of Trainees: {entity['traineeCount']}
            - Sectors: {', '.join(entity['sectors'])}
            - Cities: {', '.join(entity['cities'])}
            """
        documents.append(Document(text=entities_text))
        
        # Top Students document
        students_text = "Top Performing Students in Tourism:\n"
        for student in self.api_data['topStudents']:
            students_text += f"""
            Student: {student['name']}
            - Institute: {student['institute']}
            - GPA: {student['gpa']}
            - English Level: {student['english_level']}
            """
        documents.append(Document(text=students_text))
        
        # Create index from structured documents
        self.api_index = VectorStoreIndex.from_documents(documents)

    def get_api_response(self, query: str) -> str:
        """Get response for API-related queries with tourism-specific context."""
        if not self.api_index:
            raise Exception("API index not initialized. Please initialize with API data first.")
        
        # Add tourism-specific context to the query
        enhanced_query = f"""
        Context: This is a tourism industry database containing information about:
        - Tourism metrics and statistics
        - Top performing tourism entities and their details
        - Outstanding students in tourism-related education
        
        User Question: {query}
        
        Please provide a clear and relevant answer based on the available tourism data.
        """
        
        chat_engine = self.api_index.as_chat_engine(
            chat_mode="condense_plus_context",
            verbose=True
        )
        response = chat_engine.chat(enhanced_query)
        return str(response)

    def get_pdf_response(self, query: str) -> str:
        """Get response for PDF-related queries."""
        if not self.pdf_index:
            raise Exception("PDF index not initialized. Please initialize with PDF data first.")
        
        chat_engine = self.pdf_index.as_chat_engine(
            chat_mode="condense_plus_context",
            verbose=True
        )
        response = chat_engine.chat(query)
        return str(response)

    def get_response(self, query: str, source: str = "both") -> Dict[str, str]:
        """
        Get response from specified source(s).
        source can be "pdf", "api", or "both"
        """
        responses = {}
        
        if source in ["pdf", "both"] and self.pdf_index:
            try:
                responses["pdf"] = self.get_pdf_response(query)
            except Exception as e:
                responses["pdf_error"] = str(e)
        
        if source in ["api", "both"] and self.api_index:
            try:
                responses["api"] = self.get_api_response(query)
            except Exception as e:
                responses["api_error"] = str(e)
        
        return responses
