# MVP toolings
- smolagents + MCP pathway

# intelligent Edge Data Agent (EDA)
EDA is an on-premises data analytics solution that leverages state-of-the-art large language model (LLM) code generation to dynamically create a local agent service. Rather than requiring users to upload raw data to cloud platforms, EDA keeps everything local, providing a privacy-preserving and efficient way to interact with and analyze data.

EDA converts a user’s own data into a local on-demand agent service by leveraging the latest auto code generation capabilities of LLMs
- Agent code is generated on the fly the first time the user interacts with the database
- User can also serve EDA usage by standardized APIs or function callings from LLMs once an EDA project is initiated
- No coding knowledge is required for users to build an RAG+agent system
- In contrast to other RAG systems, the user do not uploading raw data to any online platforms

EDA leverages state-of-the-art LLM code-generation capabilities and adapts to the user’s database type
- Unlike cloud-based RAG systems, which require users to upload data to a cloud platform for summarization, retrieval, or other tasks, EDA keeps the process local 
- The process including metadata generation, building the retrieval system 
- The goal is to allow users to interact with, digest, or serve their own data on-demand without prior application development

Key solution roadmap:
Assumption #1: The accuracy and robustness of code generation from LLMs keeps improving quickly over time (SWEBench https://www.swebench.com/) 
Assumption #2: The accuracy is further improved by narrowing the scope of work (e.g., coding specifically for building a RAG system) and the first-hand knowledge database from the owner of the data
Assumption #3: Instead of building up a generalized RAG system for all the users and types of database, it’s more likely easier to generate an application on-demand given the task of user-data interaction is simple and straightforward (e.g. local Q&A, plot a figure, etc.)

Documentation, architecture and demo are initiated – the implementation is on-going

[![Watch the demo](https://img.youtube.com/vi/gd279uKtv8U/0.jpg)](https://www.youtube.com/watch?v=gd279uKtv8U)


Data type 
---
Process some sensoring data given
User input: "here is an example of some log file data in my program "log.txt", can you help debug it?"
EDA response: "can you provide more information about the ?"
