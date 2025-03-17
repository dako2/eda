#worker and consumer should be isolated
import shutil
import os
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.llms import MockLLM
Settings.llm = MockLLM()
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize the Settings with specific components
class InfiniEdgeDataFormat:
    def __init__(self, input_data_folder_directory, cache_storage_path, api_yaml_file_path, emb_model_name):
        self.input_data_folder_directory = input_data_folder_directory
        self.cache_storage_path = cache_storage_path
        self.api_yaml_file_path = api_yaml_file_path
        self.rag_description = {"emb_model_name": emb_model_name}
        self.rag_py_path = os.path.join(input_data_folder_directory, "rag.py")  # Default location for rag.py

    def __description__(self):
        # Gather data folder information
        folder_structure = []
        file_types = set()
        total_size = 0

        for root, _, files in os.walk(self.input_data_folder_directory):
            for file in files:
                file_path = os.path.join(root, file)
                folder_structure.append(os.path.relpath(file_path, self.input_data_folder_directory))
                file_types.add(os.path.splitext(file)[-1])
                total_size += os.path.getsize(file_path)

        # Format the description
        description = {
            "Data Folder": self.input_data_folder_directory,
            "Folder Structure": folder_structure,
            "File Types": list(file_types),
            "Total Size (bytes)": total_size,
            "Cache Storage Path": self.cache_storage_path,
            "API YAML File Path": self.api_yaml_file_path,
            "RAG Model Info": self.rag_description,
        }
        return description

    def create_rag_py(self):
        rag_script = f"""import os
from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.core.llms import MockLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Initialize the Settings with specific components
Settings.llm = MockLLM()
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

class RagSystem:
    def __init__(self, data_dir):
        self.persist_dir = os.path.join(data_dir, ".cache", "storage")
        if not os.path.exists(self.persist_dir) or not os.listdir(self.persist_dir):
            raise Exception(f"Index not found at {{self.persist_dir}}. Please ensure the index is created.")
        
        self.storage_context = StorageContext.from_defaults(persist_dir=self.persist_dir)
        self.index = load_index_from_storage(self.storage_context)
        self.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    def query(self, query, similarity_top_k=1):
        # Perform the query
        query_engine = self.index.as_query_engine(similarity_top_k=similarity_top_k)
        response = query_engine.query(query)
        
        # Compile output with source information
        output = ""
        for node in response.source_nodes:
            source = node.node.metadata.get('source', 'Unknown Source')
            text = node.node.text
            output += f"Source: {{source}}\\n{{text}}\\n\\n"
        return output

def main():
    data_dir = os.path.dirname(__file__)  # Use the current directory as the data directory
    rag_system = RagSystem(data_dir)
    print("RAG System Initialized. Ready to accept queries.")

    while True:
        query = input("Enter your query (or type 'exit' to quit): ")
        if query.lower() == "exit":
            print("Exiting RAG System.")
            break
        try:
            results = rag_system.query(query)
            print("Query Results:")
            print(results)
        except Exception as e:
            print(f"Error: {{e}}")

if __name__ == "__main__":
    main()
"""
        rag_py_path = os.path.join(self.input_data_folder_directory, "rag.py")
        with open(rag_py_path, "w") as rag_file:
            rag_file.write(rag_script)
        print(f"Independent RAG Python file created at {rag_py_path}")

    def create_openapi_yaml(self):
        yaml_content = f"""
openapi: 3.0.0
info:
  title: Local Database API for RAG Agent
  description: API for querying the local database indexed for a RAG agent.
  version: 1.0.0
servers:
  - url: http://localhost:8000
    description: Local server for the database API
paths:
  /query:
    post:
      summary: Query the database index
      description: Accepts a query string and returns relevant data from the indexed database.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
                  description: Query string for the database.
      responses:
        200:
          description: Successful query response
          content:
            application/json:
              schema:
                type: object
                properties:
                  results:
                    type: array
                    description: List of relevant results from the database.
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                          description: Unique identifier for the result.
                        content:
                          type: string
                          description: Content of the result.
        400:
          description: Bad request
        500:
          description: Internal server error
  /index:
    post:
      summary: Reindex the database
      description: Re-indexes the database to ensure up-to-date information for RAG queries.
      requestBody:
        required: false
      responses:
        200:
          description: Indexing successful
        500:
          description: Internal server error
"""
        os.makedirs(os.path.dirname(self.api_yaml_file_path), exist_ok=True)  # Ensure the folder exists
        with open(self.api_yaml_file_path, "w") as yaml_file:
            yaml_file.write(yaml_content)
        print(f"OpenAPI YAML created at {self.api_yaml_file_path}")

class Worker(InfiniEdgeDataFormat):
    def __init__(self, input_data_folder_directory, emb_model_name):
        # Derive cache path and YAML file path from the data directory
        cache_storage_path = os.path.join(input_data_folder_directory, ".cache")
        api_yaml_file_path = os.path.join(cache_storage_path, "api.yaml")
        super().__init__(input_data_folder_directory, cache_storage_path, api_yaml_file_path, emb_model_name)
        
        self.llm = Settings.llm
        self.embed_model = Settings.embed_model
        self.persist_dir = os.path.join(self.cache_storage_path, "storage")

        if not os.path.exists(self.persist_dir) or not os.listdir(self.persist_dir):
            print("Index not found, creating a new one...")
            self.create_index()
        else:
            print("Loading existing index...")
            self.load_index()

    def create_index(self):
        documents = SimpleDirectoryReader(self.input_data_folder_directory).load_data()
        self.index = VectorStoreIndex.from_documents(documents)
        os.makedirs(self.cache_storage_path, exist_ok=True)  # Ensure the cache directory exists
        self.index.storage_context.persist(persist_dir=self.persist_dir)
        print(f"Index created and saved to {self.persist_dir}")

    def load_index(self):
        storage_context = StorageContext.from_defaults(persist_dir=self.persist_dir)
        self.index = load_index_from_storage(storage_context)
        print(f"Index loaded from {self.persist_dir}")

    def delete(self):
        if os.path.exists(self.cache_storage_path):
            try:
                shutil.rmtree(self.cache_storage_path)
                os.remove("./demo/rag.py")
                print(f"Cache folder at '{self.cache_storage_path}' has been deleted.")
            except Exception as e:
                print(f"Error while deleting cache folder: {e}")
        else:
            print(f"Cache folder at '{self.cache_storage_path}' does not exist.")

if __name__ == "__main__":
    data_dir = "./demo"  # Data folder
    emb_model_name = "sentence-transformers/all-MiniLM-L6-v2"

    # Initialize the worker
    worker = Worker(data_dir, emb_model_name)

    # Create the OpenAPI YAML file
    worker.create_openapi_yaml()

    # Generate the RAG Python script
    worker.create_rag_py()

    # Print the description
    description = worker.__description__()
    print("System Description:")
    for key, value in description.items():
        print(f"{key}: {value}")
  