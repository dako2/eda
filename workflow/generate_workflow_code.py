import os
import yaml
import litellm
import json 
from pathlib import Path

litellm.model = "xai/grok-3-latest"  # or any supported model

PROMPT_DIR = "llm_prompts"

def auto_generate_prompt(name, description):
    # Use GPT to generate a clean system prompt for the step
    messages = [
        {"role": "system", "content": "You are an expert prompt writer for LLM function agents."},
        {"role": "user", "content": f"""
Write a system prompt for an LLM agent named `{name}`.

Its goal is:
{description}

This LLM will receive input as a dictionary (e.g. `data`) and should return a modified `data` dictionary.

Your response must include:
- The agent’s role
- Detailed instruction for what it should do
- What the input looks like
- What the expected output looks like
"""}
    ]
    response = litellm.completion(model=litellm.model, messages=messages)
    return response["choices"][0]["message"]["content"].strip()

def build_prompts(workflow_path: str, save: bool = True):
    with open(workflow_path, "r") as f:
        workflow = yaml.safe_load(f)

    prompts = {}
    os.makedirs(PROMPT_DIR, exist_ok=True)

    for step in workflow["steps"]:
        name = step["step"]
        desc = step["description"]
        prompt_path = f"{PROMPT_DIR}/{name}.yaml"

        if os.path.exists(prompt_path):
            print(f"📄 Loading existing prompt: {prompt_path}")
            with open(prompt_path, "r") as f:
                prompts[name] = yaml.safe_load(f)
        else:
            print(f"✨ Generating new system prompt for: {name}")
            content = auto_generate_prompt(name, desc)
            prompt_obj = {
                "name": name,
                "role": "system",
                "content": content
            }
            prompts[name] = prompt_obj

            if save:
                with open(prompt_path, "w") as f:
                    yaml.dump(prompt_obj, f, allow_unicode=True)
                print(f"✅ Saved new prompt: {prompt_path}")

    return prompts

def run_llm_step(prompt: dict, user_input: dict):
    messages = [
        {"role": prompt["role"], "content": prompt["content"]},
        {"role": "user", "content": f"{user_input}"}
    ]
    response = litellm.completion(model=litellm.model, messages=messages)
    return response["choices"][0]["message"]["content"].strip()

def run_workflow(workflow_path: str, initial_data_path: str, prompts: dict):
    with open(workflow_path, "r") as f:
        workflow = yaml.safe_load(f)

    data = initial_data

    for step in workflow["steps"]:
        name = step["step"]
        prompt = prompts[name]

        print(f"\n⚙️ Running step: {name}")
        result = run_llm_step(prompt, data)
        print(f"🔁 Output: {result}")

        try:
            parsed = json.loads(result)
            if isinstance(parsed, dict):
                data.update(parsed)
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error in step {name}: {e}")
            print(f"🔍 Raw output: {result}")

    return data

if __name__ == "__main__":
    workflow_file = "pdf_retrieval_workflow.yaml"

    # 1. Generate system prompts from workflow (optionally save)
    prompts = build_prompts(workflow_file, save=True)

    # 2. Initial input for the first step
    initial_input = "../sandbox/data/childbook/Oumas-Amazing-Flowers_English.pdf"

    # 3. Run the entire LLM workflow
    final_output = run_workflow(workflow_file, initial_input, prompts)

    print("\n🎉 Final Output:\n", final_output)
