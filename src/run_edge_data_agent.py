from pathlib import Path
from eda_sample import eda_by_smol

def run_edge_data_agent(agent_card: str, user_input: str, task_path: Path) -> str:
    """
    A simple placeholder RAG agent:
    - Loads .txt files (excluding input.txt) from the task folder
    - Searches for keyword matches
    - Returns a mock answer with matching lines
    """
    print("🔍 [run_edge_data_agent] Processing task:", task_path.name)
    
    context_chunks = []
    
    for file in task_path.iterdir():
        if file.suffix == ".txt" and file.name != "input.txt":
            try:
                content = file.read_text(encoding="utf-8")
                context_chunks.append(f"{file.name}:\n{content}")
            except Exception as e:
                print(f"⚠️ Could not read {file.name}: {e}")

    # Combine into one big context and search for user query keywords
    combined_context = "\n\n".join(context_chunks)
    keywords = user_input.lower().split()
    matching_lines = [
        line for line in combined_context.splitlines()
        if any(k in line.lower() for k in keywords)
    ]

    return (
        f"🧠 [Mock Agent Answer]\n"
        f"Query: {user_input.strip()}\n"
        f"Found {len(matching_lines)} match(es):\n" +
        "\n".join(matching_lines[:5])  # Limit for readability
    )
