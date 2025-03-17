from setuptools import setup, find_packages

setup(
    name="eda-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyYAML",
        "smolagents",
        "llama-index",
        "llama-index-embeddings-huggingface"
    ],
    entry_points={
        'console_scripts': [
            'eda=eda_cli:main',
        ],
    },
    python_requires='>=3.12',
    author="Your Name",
    author_email="your.email@example.com",
    description="CLI tool for EDA and RAG tasks with smolagents",
    url="https://yourprojecturl.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
