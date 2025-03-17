"""
pip install llama-index
pip install llama-index-embeddings-huggingface
"""
import os
from smolagents import Tool
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.core.llms import MockLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Initialize Settings with the desired LLM and embedding model
Settings.llm = MockLLM()
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

class RAGTool(Tool):
    name = "rag_tool"
    description = "A simple RAG tool that performs retrieval augmented generation on a document corpus."
    inputs = {
        "data_dir": {
            "type": "string",
            "description": "The directory of data to be retrieved."
        },
        "question": {
            "type": "string",
            "description": "The query question for retrieval."
        },
        "similarity_top_k": {
            "type": "string",
            "description": "The number of top similar documents to retrieve (provided as a string to be cast to an integer)."
        }
    }
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def forward(self, data_dir: str, question: str, similarity_top_k: str) -> str:
        self.data_dir = data_dir
        self.llm = Settings.llm 
        self.embed_model = Settings.embed_model
        persist_dir = os.path.join(data_dir, '.cache/storage')

        # Create or load the index based on the persisted directory
        if not os.path.exists(persist_dir) or not os.listdir(persist_dir):
            print("Index not found, creating a new one...")
            documents = SimpleDirectoryReader(data_dir).load_data()
            self.index = VectorStoreIndex.from_documents(documents)
            self.index.storage_context.persist(persist_dir=persist_dir)
            self.save_to_mcp(data_dir)
        else:
            print("Loading existing index...")
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            self.index = load_index_from_storage(storage_context)
            
        # Convert similarity_top_k to integer
        k = int(similarity_top_k)
        query_engine = self.index.as_query_engine(similarity_top_k=k)
        response = query_engine.query(question)

        # Compile output with source information
        output = "-----\n"
        for node in response.source_nodes:
            #source = node.node.metadata.get('source', 'Unknown Source')
            text_fmt = node.node.get_content().strip().replace("\n", " ")
            output += f"Text:\t {text_fmt}\n"
            output += f"Metadata:\t {node.node.metadata}"
            output += f"Score:\t {node.score:.3f}"
        return output
    
    def save_to_mcp(self, data_dir:str) -> str:
        """Saves the RAG tool's retrieval script for standalone execution."""
        retrieval_code = f"""

import os
from mcp.server.fastmcp import FastMCP
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage, Settings
from llama_index.core.llms import MockLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Configure LlamaIndex settings
Settings.llm = MockLLM()
Settings.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Instantiate the MCP server with a descriptive name
mcp = FastMCP("RAGTool Server")

# Wrap the query functionality as an MCP tool.
@mcp.tool()
def query_document(question: str, similarity_top_k: int = 3) -> str:
    \"\"\"
    Query the document index with a given question and optional similarity threshold.
    \"\"\"
    class RAGTool:
        def __init__(self,):
            self.data_dir = os.path.dirname(__file__)
            self.persist_dir = os.path.join(self.data_dir, 'storage')
            
            storage_context = StorageContext.from_defaults(persist_dir=self.persist_dir)
            self.index = load_index_from_storage(storage_context)
            print("Loading existing index...")

        def query(self, question: str, similarity_top_k: int = 3) -> str:
            query_engine = self.index.as_query_engine(similarity_top_k=similarity_top_k)
            response = query_engine.query(question)
            return  ".join([node.node.get_content().strip() for node in response.source_nodes])

    rag_tool = RAGTool()
    return rag_tool.query(question, similarity_top_k)

print("building mcp server")

if __name__ == "__main__":
    # Start the MCP server using stdio transport (or choose another transport if needed)
    mcp.run(transport="stdio")
        """
        filepath = os.path.join(data_dir, '.cache/rag_mcp.py')
        with open(filepath, "w") as file:
            file.write(retrieval_code)
        print(f"RAG script saved in {filepath}")
        return f"successfully save a rag retrieval mcp server code to {filepath}"


if __name__ == "__main__":
    # Instantiate the RAGTool with your data directory
    tool = RAGTool(data_dir='./')
    # Sample question and top_k (as a string)
    question = "summarize the document"
    response = tool.forward(question, "3")
    print(response)
    