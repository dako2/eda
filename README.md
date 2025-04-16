# Edge Data Agent (EDA)
EDA is an on-premises data analytics solution by leveraging LLM's code generation capability.

Rather than requiring users to upload raw data to cloud platforms, EDA keeps everything local, providing a privacy-preserving and efficient way to interact with and analyze data.

EDA converts a user’s own data into a local on-demand agent service by leveraging the latest auto code generation capabilities of LLMs
- Agent code is generated on the fly the first time the user interacts with the database
- No coding knowledge (maybe even no installation needed if possible) is required for users to build and use
- In contrast to centralized AI platform, the user do not need uploading raw data
- The goal is to allow users to interact with, digest, or serve their own data on-demand without prior application development

# Installation
(WIP)

# Sandbox Data
sandbox/data/ stores the data, agent_card, input for evaluation
run local_evaluation.py to evaluate the agent performance

=======
# MVP toolings
Currently, we are leveraging smolagents and llamaindex framework: read / write files from the local directory. Agent for writing up the retrieval code


# Assumptions
1. The accuracy and robustness of LLM code generation improves to human level (SWEBench https://www.swebench.com/)
2. The cost of autonomous coding goes to negligible
3. The accuracy can be further improved by local knowledge of the data base and the information of user query history