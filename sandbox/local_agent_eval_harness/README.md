# Local Agent Eval Harness

This harness runs the same tasks against:
1) A **General LLM** (no local file access)
2) A **Local Agent** (allowed to read local files & use tools)

and scores them against the ground truth shipped with the data packs.

## Quick Start
1. Unzip the evaluation packs into a folder, e.g.
   - `/data/LocalAgentEvalSuite/` (Pack 1)
   - `/data/LocalAgentEvalSuite_Pack2/`
   - `/data/LocalAgentEvalSuite_Pack3/`
   - `/data/LocalAgentEvalSuite_Pack4/`
2. Implement the providers:
   - `providers/general_llm.py`: call your hosted model (no local file access).
   - `providers/local_agent.py`: call your local agent with file access.
3. Run the harness:
```bash
python harness.py --packs "/data" --out "report.json"
```
4. Inspect `report.json` and the per-task logs in `runs/`.

## Scoring
- Each task expects a **JSON** answer with specific keys. We compare to `answers*.json`.
- Score = exact match (% of keys matching expected values). Non-scalars are compared as sets/lists where sensible.
- We log both the model's raw text and parsed JSON for debugging.

## Adding/Removing Tasks
- Edit `tasks.py`. Each task defines:
  - `pack_glob` (directory name pattern)
  - `prompt` (input string sent to both providers)
  - `answer_path` (relative path to ground-truth answers file)
  - `answer_key_path` (JSON pointer list to the sub-answer we compare against)
  - `extractor` (optional) to post-process model JSON to a comparable shape.


### Evaluation Results

| Task                         | General LLM | Local Agent | Δ (Agent − LLM) |
|-----------------------------|------------:|------------:|----------------:|
| p1_finance_invoice_match    | 0.33        | 1.00        | 0.67            |
| p1_hr_post_termination      | 0.00        | 1.00        | 1.00            |
| p1_ops_spike                | 0.00        | 1.00        | 1.00            |
| p2_emails_discount_thread   | 0.00        | 1.00        | 1.00            |
| p2_audio_merge              | 0.17        | 1.00        | 0.83            |
| p2_finance_fx               | 0.00        | 0.40        | 0.40            |
| p3_ocr_invoice              | 0.00        | 1.00        | 1.00            |
| p3_sql_recon                | 0.00        | 1.00        | 1.00            |
| p4_eml_attachments          | 0.00        | 1.00        | 1.00            |
| p4_xlsx_summary             | 0.00        | 0.00        | 0.00            |
| **Averages**                | **0.05**    | **0.84**    | **0.79**        |
