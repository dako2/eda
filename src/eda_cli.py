#!/usr/bin/env python3
import argparse
import subprocess
import os
import venv
import sys
import yaml
import datetime
import threading

from smolagents import CodeAgent, LiteLLMModel, ToolCallingAgent
# Tools for data processing
from tools.tool_rag import RAGTool, load_registry
from tools.tool_sqlite import SQLiteTool
from tools.tool_file_writer import FileWriter
from tools.tool_directory_analyzer import DirectoryAnalyzer
# Registry management tool (implements update, list, clear)
from tools.tool_registry_manager import RegistryManager

# Default model and constants
DEFAULT_MODEL = "gemini/gemini-pro"
MODEL_ENV_VAR = "EDA_MODEL"
RAG_CACHE_DIR = ".cache"
RAG_MCP_SCRIPT_NAME = "rag_mcp.py"
VENV_NAME = "eda_venv"

def create_venv():
    """Creates a Python 3.12 virtual environment."""
    venv_path = os.path.join(os.getcwd(), VENV_NAME)
    if not os.path.exists(venv_path):
        print(f"Creating virtual environment in {venv_path}...")
        try:
            venv.create(venv_path, with_pip=True)
            print("Virtual environment created successfully.")
        except Exception as e:
            print(f"Error creating virtual environment: {e}")
            sys.exit(1)
    else:
        print(f"Virtual environment already exists in {venv_path}.")
    return venv_path

def install_dependencies(venv_path):
    """Installs the required dependencies in the virtual environment."""
    pip_executable = os.path.join(venv_path, 'bin', 'pip')
    if sys.platform == "win32":
        pip_executable = os.path.join(venv_path, 'Scripts', 'pip.exe')
    dependencies = ["PyYAML", "smolagents", "llama-index", "llama-index-embeddings-huggingface"]
    print("Installing dependencies...")
    try:
        subprocess.check_call([pip_executable, "install"] + dependencies)
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def set_model(model_name):
    """Sets the model name as an environment variable."""
    os.environ[MODEL_ENV_VAR] = model_name
    print(f"Model set to: {model_name}")

def run_rag_all(query: str, similarity_top_k: str = "3") -> str:
    """
    Runs the RAG process for the given query on all data directories listed in the registry,
    and aggregates the outputs.
    """
    registry = load_registry()
    if not registry:
        return "No registry entries found. Please update the registry first."

    results = []
    rag_tool = RAGTool()
    
    for entry in registry:
        data_dir = entry.get("data_directory")
        if data_dir:
            output = rag_tool.forward(data_dir, query, similarity_top_k)
            results.append(f"Results for data directory '{data_dir}':\n{output}\n")
        else:
            results.append("Skipping an entry with no valid data_directory.\n")
    
    return "\n".join(results)

def run_agent(user_message):
    """Runs the smolagents agent with the given user message."""
    print(f"Running agent with message: '{user_message}'")
    model_name = os.environ.get(MODEL_ENV_VAR, DEFAULT_MODEL)
    model = LiteLLMModel(model_id=model_name, temperature=0.2)

    eda_agent = ToolCallingAgent(
        tools=[RAGTool(), RegistryManager()],
        model=model,
        name="eda_agent",
        description="Explorative data agent",
        verbosity_level=2,
    )

    eda_agent.run(user_message)

def run_mcp_all(code_directory: str):
    """
    Launches the MCP server as a separate process and streams its output.
    It uses the command: mcp dev mcp_server.py.
    """
    mcp_server_script = os.path.join("mcp_server.py")
    if not os.path.exists(mcp_server_script):
        print(f"Error: MCP server script not found at {mcp_server_script}.")
        sys.exit(1)
    
    # Set unbuffered environment variable for the subprocess.
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    
    try:
        # Correctly separate the command and its arguments.
        proc = subprocess.Popen(
            ["mcp", "dev", mcp_server_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,  # line-buffered
            text=True,
            env=env
        )
        print("MCP server started as a separate process. Streaming logs below:")
        
        # Stream stdout line by line.
        for line in iter(proc.stdout.readline, ''):
            print(line, end='')
        
        # Optionally, also print stderr lines.
        for err_line in iter(proc.stderr.readline, ''):
            print(err_line, end='')
        
        proc.stdout.close()
        proc.stderr.close()
        proc.wait()
    except Exception as e:
        print(f"Error launching MCP server process: {e}")


def main():
    parser = argparse.ArgumentParser(description="EDA CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # install command
    install_parser = subparsers.add_parser("install", help="Setup the Python virtual environment and install dependencies")

    # model command
    model_parser = subparsers.add_parser("model", help="Set the model to be used")
    model_parser.add_argument("model_name", help="Name of the model (e.g., grok-2-latest)")

    # rag command: now only requires query (registry is loaded to get all data directories)
    rag_parser = subparsers.add_parser("rag", help="Run the RAG process for all data directories in the registry with a query")
    rag_parser.add_argument("query", help="Query for the RAG tool")
    rag_parser.add_argument("--similarity_top_k", default="3",
                            help="Number of similar docs to retrieve (default: 3)")
    rag_parser.add_argument("--code_directory", default=os.getcwd(),
                            help="Path to the code directory (default: current directory)")
    rag_parser.add_argument("--data_format", default="unknown",
                            help="Format of the data (e.g., pdf, csv, txt; default: unknown)")

    # run agent command
    agent_parser = subparsers.add_parser("run", help="Run the agent with a user message")
    agent_parser.add_argument("user_message", nargs='+', help="The message to send to the agent")

    # mcp command: now launches the MCP server as a subprocess
    mcp_parser = subparsers.add_parser("mcp", help="Start the MCP server as a separate process")
    mcp_parser.add_argument("--code_directory", default=os.getcwd(),
                            help="Path to the code directory (default: current directory)")

    # registry command with subcommands (list, clear)
    registry_parser = subparsers.add_parser("registry", help="Manage the data source registry via RegistryManager")
    registry_subparsers = registry_parser.add_subparsers(dest="registry_command", help="Registry commands")
    registry_subparsers.add_parser("list", help="List all data sources in the registry")
    registry_subparsers.add_parser("clear", help="Clear the data source registry")

    args = parser.parse_args()

    if args.command == "install":
        venv_path = create_venv()
        install_dependencies(venv_path)
        print(f"\nRemember to activate the virtual environment before running other commands:\n"
              f"On Linux/macOS: source {VENV_NAME}/bin/activate\nOn Windows: .\\{VENV_NAME}\\Scripts\\activate")
    elif args.command == "model":
        set_model(args.model_name)
    elif args.command == "rag":
        result = run_rag_all(args.query, args.similarity_top_k)
        print(result)
    elif args.command == "mcp":
        run_mcp_all(args.code_directory)
    elif args.command == "run":
        user_message = " ".join(args.user_message)
        run_agent(user_message)
    elif args.command == "registry":
        registry_tool = RegistryManager()
        if args.registry_command == "list":
            result = registry_tool.forward("list")
            print(result)
        elif args.registry_command == "clear":
            result = registry_tool.forward("clear")
            print(result)
        else:
            print("Please specify a valid registry subcommand (list or clear).")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
