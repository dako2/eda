"""from smolagents import ToolCallingAgent, LiteLLMModel
from tools.tool_sqlite import SQLiteTool
from tools.tool_directory_analyzer import DirectoryAnalyzer

model_name = "xai/grok-2-latest"
model = LiteLLMModel(
    model_id=model_name,
    temperature=0.2,
    #max_tokens=4096,
)
my_agent = ToolCallingAgent(
    tools=[SQLiteTool(), DirectoryAnalyzer()],
    model=model,
    # ... other agent settings
)
my_agent.run("check my sql data under ../examples/data/sql_data")
"""

from smolagents import ToolCallingAgent, LiteLLMModel
from tools.tool_rag import RAGTool
from tools.tool_registry_manager import RegistryManager

agent = ToolCallingAgent(
    tools=[RAGTool(), RegistryManager()],
    model=LiteLLMModel(model_id="xai/grok-2-latest")
)

task = "Run rag with data_dir='../examples/data/pdf', question='summarize the document', top_k=3"
response = agent.run(task)
print(response)
