# The intelligent Edge Data Agent (EDA)
EDA is an on-premises data analytics solution by leveraging LLM's code generation capability.

Rather than requiring users to upload raw data to cloud platforms, EDA keeps everything local, providing a privacy-preserving and efficient way to interact with and analyze data.

EDA converts a user’s own data into a local on-demand agent service by leveraging the latest auto code generation capabilities of LLMs
- Agent code is generated on the fly the first time the user interacts with the database
- No coding knowledge (maybe even no installation needed if possible) is required for users to build and use
- In contrast to centralized AI platform, the user do not need uploading raw data
- The goal is to allow users to interact with, digest, or serve their own data on-demand without prior application development

Assumption #1: The accuracy and robustness of code generation from LLMs keeps improving quickly over time (SWEBench https://www.swebench.com/) 
Assumption #2: The accuracy is further improved by narrowing the scope of work (e.g., coding specifically for building a RAG system) and the first-hand knowledge database from the owner of the data
Assumption #3: Instead of building up a generalized RAG system for all the users and types of database, it’s more likely easier to generate an application on-demand given the local knowledge and user intention (e.g. local Q&A, plot a figure, etc.)

# Installation
python -m venv venv

source venv/bin/activate

cd src

pip install -e .

# Usage
eda run "summarize the data in ../examples/data/pdf"

eda registry list

eda rag "the title of the document?"

eda mcp
=======
# MVP toolings
Currently, we are leveraging smolagents and llamaindex framework: read / write files from the local directory. Agent for writing up the retrieval code
>>>>>>> 765737d922ece86df2ef0089f57607144d797f70
