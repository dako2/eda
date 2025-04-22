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

def run_workflow(workflow_path: str, initial_data: dict, prompts: dict):
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
    workflow_file = "presentation_workflow.yaml"
    workflow_file = "image_search_workflow.yaml"

    # # 1. Generate system prompts from workflow (optionally save)
    # prompts = build_prompts(workflow_file, save=True)

    # # 2. Initial input for the first step
    # initial_input = {
    #     "speaker_notes": "原子结构的构成是由原子核与核外电子构成的，而原子核外电子的发现是在1897年，由汤姆逊的出色实验得到的。汤姆逊的实验过程是这样的，他将一块涂有硫化锌的小玻璃片，放在阴极射线所经过的路途上，看到硫化锌会发闪光。这说明硫化锌能显示出阴极射线的“径迹”。他发现在一般情况下，阴极射线是直线行进的，但当在射击线管的外面加上电场，或用一块蹄形磁铁跨放在射线管的外面，结果发现阴极射线一都发生了偏折。根据其偏折的方向，不难判断出带电的性质。汤姆逊在1897年得出结论：这些“射线”不是以太波，而是带负电的物质粒子。但他反问自已：“这些粒子是什么呢？它们是原子还是分子，还是处在更细的平衡状态中的物质？“这需要作更精细的实验，当时还不知道比原子更小的东西，因此汤姆逊假定这是一种被电离的原子，即带负电的“离子”。他要测量出这种“离子”的质量。为此，他设计了一系列即简单又巧妙的实验：首先，设计单独的电场或磁场都能使带电体偏转，而磁场对粒子施加的力是与粒子的速度有关的。汤姆逊对粒子同时施加一个电场和磁场，并调节到电场和磁场所造成的粒子的偏转互相抵消，让粒子仍作直线运动。这样，从电场和磁场的强度比值就能算出粒子运动速度。而速度一旦找到后，单靠磁偏转或者电偏转就可以测出粒子的电荷与质量的比值。汤姆逊用这种方法来测定“微粒”电荷与质量之比值。他发现这个比值和气体的性质无关，并且该值比起电解质中氢离子的比值（这是当时已知的最大量）还要大得多，这说明这种粒子的质量比氢原子的质量要小得多。前者大约是后者的二千分之一。"
    # }

    # # 3. Run the entire LLM workflow
    # final_output = run_workflow(workflow_file, initial_input, prompts)

    # print("\n🎉 Final Output:\n", final_output)

    slides_file = "slides.json"  # Update path if needed

    # === STEP 1: Load Slides JSON ===
    with open(slides_file, "r", encoding="utf-8") as f:
        slide_data = json.load(f)
        slides = slide_data["slides"]


    # === STEP 2: Build Prompts ===
    prompts = build_prompts(workflow_file, save=True)

    # === STEP 3: Run Workflow for Each Slide ===
    all_outputs = []
    for idx, slide in enumerate(slides):
        speaker_notes = slide.get("script") or slide.get("speaker_notes") or ""
        if not speaker_notes.strip():
            print(f"⚠️ Skipping empty script at index {idx}")
            continue

        print(f"\n🚀 Running workflow for Slide {idx+1}...")

        input_data = {"speaker_notes": speaker_notes}
        result = run_workflow(workflow_file, input_data, prompts)
        
        # Optionally attach the result to the slide
        slide["generated"] = result
        all_outputs.append(result)

    # === STEP 4: Save Updated Slides (optional) ===
    output_path = Path(slides_file).with_name("slides_with_images.json")
    slide_data["slides"] = slides
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(slide_data, f, ensure_ascii=False, indent=2)

    print("\n✅ All slides processed. Output saved to:", output_path)
