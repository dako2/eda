#!/usr/bin/env python3

import argparse
import subprocess
import os
import venv
import sys
import yaml

from smolagents import CodeAgent, ToolCallingAgent, LiteLLMModel
# Assuming tools are in a 'tools' directory relative to the CLI script
from tools.tool_rag import RAGTool
from tools.tool_file_writer import FileWriter
from tools.tool_directory_analyzer import DirectoryAnalyzer

# Default model
DEFAULT_MODEL = "gemini/gemini-1.5-flash"
MODEL_ENV_VAR = "EDA_MODEL"
MODEL_API_KEY_ENV_VAR = "MODEL_API_KEY"
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

def run_rag(data_directory):
    """Runs the RAG process for the given data directory."""
    print(f"Running RAG for data in: {data_directory}")

    cache_path = os.path.join(data_directory, RAG_CACHE_DIR)
    os.makedirs(cache_path, exist_ok=True)

    model_name = os.environ.get(MODEL_ENV_VAR, DEFAULT_MODEL)

    model = LiteLLMModel(
        model_id=model_name,
        temperature=0.2,
        #max_tokens=4096,
    )

    eda_agent = CodeAgent(
        tools=[RAGTool(), DirectoryAnalyzer()],
        model=model,
        name="search",
        description="explorative data agent",
        verbosity_level=2,
    )

    message = f"Build a rag system for the database in {data_directory}"
    print(f"Running agent with message: '{message}'")
    eda_agent.run(message)
    print("RAG process completed.")

def run_agent(user_message):
    """Runs the smolagents with the given user message."""
    print(f"Running agent with message: '{user_message}'")

    model_name = os.environ.get(MODEL_ENV_VAR, DEFAULT_MODEL)

    model = LiteLLMModel(
        model_id=model_name,
        temperature=0.2,
        #max_tokens=4096,
    )

    eda_agent = CodeAgent(
        tools=[RAGTool(), DirectoryAnalyzer()],
        model=model,
        name="eda_agent",
        description="explorative data agent",
        verbosity_level=2,
    )

    eda_agent.run(user_message)
    print("Agent execution completed.")

def run_mcp():
    """Runs the MCP server using the generated RAG script."""
    print("Running MCP server...")
    data_directory = "." # Assuming the user is in the project root when running this
    rag_script_path = os.path.join(data_directory, "examples", "data", "pdf", RAG_CACHE_DIR, f"rag_mcp.py") # Adjust path if needed

    if not os.path.exists(rag_script_path):
        print(f"Error: RAG MCP script not found at {rag_script_path}. Make sure to run 'eda <data_directory>' first.")
        sys.exit(1)

    try:
        result = subprocess.run(['mcp', 'dev', rag_script_path], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"MCP server error:\n{result.stderr}")
    except FileNotFoundError:
        print("Error: 'mcp' command not found. Make sure it's installed and in your PATH.")
    except Exception as e:
        print(f"Error running MCP server: {e}")

def main():
    parser = argparse.ArgumentParser(description="EDA CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # install command
    install_parser = subparsers.add_parser("install", help="Setup the Python virtual environment and install dependencies")

    # model command
    model_parser = subparsers.add_parser("model", help="Set the model to be used")
    model_parser.add_argument("model_name", help="Name of the model (e.g., grok-2-latest)")

    # run rag command
    rag_parser = subparsers.add_parser("rag", help="Run the RAG process for a given data directory")
    rag_parser.add_argument("data_directory", help="Path to the data directory")

    # run agent with message command
    agent_parser = subparsers.add_parser("run", help="Run the agent with a user message")
    agent_parser.add_argument("user_message", nargs='+', help="The message to send to the agent")

    # mcp command
    mcp_parser = subparsers.add_parser("mcp", help="Run the MCP server")

    args = parser.parse_args()

    if args.command == "install":
        venv_path = create_venv()
        install_dependencies(venv_path)
        print(f"\nRemember to activate the virtual environment before running other commands:\nOn Linux/macOS: source {VENV_NAME}/bin/activate\nOn Windows: .\\{VENV_NAME}\\Scripts\\activate")
    elif args.command == "model":
        set_model(args.model_name)
    elif args.command == "rag":
        run_rag(args.data_directory)
    elif args.command == "run":
        user_message = " ".join(args.user_message)
        run_agent(user_message)
    elif args.command == "mcp":
        run_mcp()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()