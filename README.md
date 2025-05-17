# Semantic Operating System (Semantic OS)

![Semantic OS](https://jddwvtsq.manus.space/assets/semantic_os_logo.png)

A natural language interface for managing files and executing tasks on Linux-based systems.

## Overview

Semantic OS is a proof-of-concept system that enables natural language interactions for managing files and executing tasks on a Linux-based system. It integrates the following components:

1. **Content-Aware Storage (CAS)**: Implements a semantic file system that organizes and retrieves files based on content and context using Whoosh for metadata tagging and indexing.

2. **Local Large Language Model (LLM) Integration**: Incorporates a lightweight, local LLM (Phi-2) to interpret and respond to user queries, facilitating natural language understanding for file operations and task management.

3. **Natural Language Interface**: Provides a terminal-based chat interface that allows users to interact with the system conversationally, performing actions such as creating, moving, and deleting files by communicating in natural language.

4. **Modular Command Processing (MCP) and Agent-to-Agent (A2A) Architecture**: Designed with a modular architecture that supports MCP and A2A communication patterns, allowing for scalable and maintainable integration of various agents handling specific tasks or commands.

## Features

- **Semantic File Operations**: Find, create, open, and manage files using natural language
- **Contextual Understanding**: Maintain conversation context for follow-up queries
- **Modular Architecture**: Easily extend functionality through plugins and custom agents
- **Workflow Support**: Create and execute multi-step workflows across different agents
- **Resource Efficiency**: Optimized for running on standard hardware with reasonable memory usage

## Installation

### Prerequisites

- Linux-based operating system
- Python 3.10 or higher
- Git (for cloning the repository)
- 4GB+ RAM (8GB recommended for optimal performance)
- 2GB+ free disk space

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/semantic-os.git
   cd semantic-os
   ```

2. Create and activate a virtual environment:
   ```bash
   pip install uv
   uv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   uv sync --all-extras
   ```

4. Download the language model:
   ```bash
   uv run python scripts/download_model.py
   ```

5. Run Semantic OS:
   ```bash
   uv run python main.py
   ```

## Usage

Semantic OS understands a wide range of natural language commands. Here are some examples:

### File Operations

- **Finding files**:
  ```
  Find files related to python programming
  Search for documents about semantic computing
  Look for files I edited yesterday
  ```

- **Creating files**:
  ```
  Create a new text file called notes.txt
  Make a new Python script for web scraping
  ```

- **Opening files**:
  ```
  Open the presentation about semantic OS
  Show me the latest report
  ```

### Advanced Usage

- **Complex queries**:
  ```
  Find all Python files related to data analysis and create a summary
  Search for documents about climate change and extract key points
  ```

- **Workflows**:
  ```
  Create a workflow to find all research papers, extract their abstracts, and generate a summary
  Set up a daily task to organize my downloads folder
  ```

## Project Structure

```
semantic-os/
├── docs/                  # Documentation
│   ├── architecture_design.md
│   ├── documentation.md
│   └── requirements_analysis.md
├── src/                   # Source code
│   ├── cas/               # Content-Aware Storage
│   │   ├── cas_api.py
│   │   ├── extractors.py
│   │   ├── file_indexer.py
│   │   ├── metadata_store.py
│   │   └── semantic_index.py
│   ├── interface/         # Natural Language Interface
│   │   ├── input_processor.py
│   │   ├── interface_api.py
│   │   ├── response_formatter.py
│   │   ├── session_manager.py
│   │   └── terminal_ui.py
│   ├── llm/               # Local LLM Integration
│   │   ├── context_manager.py
│   │   ├── inference_engine.py
│   │   ├── llm_api.py
│   │   ├── model_manager.py
│   │   └── prompt_engineer.py
│   ├── mcp/               # Modular Command Processing
│   │   ├── agent_registry.py
│   │   ├── command_processor.py
│   │   ├── command_router.py
│   │   ├── mcp_api.py
│   │   ├── message_bus.py
│   │   └── workflow_engine.py
│   ├── cas_demo.py        # CAS demonstration
│   ├── interface_demo.py  # Interface demonstration
│   ├── llm_demo.py        # LLM demonstration
│   └── mcp_demo.py        # MCP demonstration
├── tests/                 # Test scripts
│   ├── integration_test.py
│   └── validation_tests.py
├── main.py                # Main entry point
├── pyproject.toml       # Project dependencies
└── README.md              # This file
```

## Documentation

For detailed documentation, visit our [website](https://jddwvtsq.manus.space) or check the `docs/` directory.

## Extensibility

Semantic OS is designed to be extensible through a plugin architecture. You can extend the system by:

1. Adding new content extractors for different file types
2. Creating custom command processors for specific tasks
3. Developing new agents with specialized capabilities
4. Implementing custom workflows for complex operations

See the [Extensibility Guide](https://jddwvtsq.manus.space/#extend) for detailed instructions.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Hugging Face Transformers](https://github.com/huggingface/transformers) for LLM support
- [Whoosh](https://github.com/mchaput/whoosh) for indexing and search functionality
- [Textual](https://github.com/Textualize/textual) for the terminal UI
- [Microsoft Phi-2](https://github.com/microsoft/Phi-2) for the lightweight LLM model
