# Edge Data Agent (EDA)
EDA is an on-premises data analytics solution that leverages state-of-the-art large language model (LLM) code generation to dynamically create a local data agent service. Rather than requiring users to upload raw data to cloud platform, EDA keeps everything local, providing a privacy-preserving and efficient way to interact with and analyze data.

EDA studies how we efficiently and effectively feed the local knowledge and user intention into LLMs by retrieval, memory, and then generating the corresponding agent service code. 

EDA converts a user’s own data into a local on-demand agent service by leveraging the latest auto code generation capabilities of LLMs
- Agent code is generated on the fly the first time the user interacts with the database
- No coding knowledge (maybe even no installation needed if possible) is required for users to build and use
- In contrast to centralized AI platform, the user do not need uploading raw data
- The goal is to allow users to interact with, digest, or serve their own data on-demand without prior application development

Assumption #1: The accuracy and robustness of code generation from LLMs keeps improving quickly over time (SWEBench https://www.swebench.com/) 
Assumption #2: The accuracy is further improved by narrowing the scope of work (e.g., coding specifically for building a RAG system) and the first-hand knowledge database from the owner of the data
Assumption #3: Instead of building up a generalized RAG system for all the users and types of database, it’s more likely easier to generate an application on-demand given the local knowledge and user intention (e.g. local Q&A, plot a figure, etc.)

# MVP toolings
Currently, we are leveraging smolagents and llamaindex framework: read / write files from the local directory. Agent for writing up the retrieval code
