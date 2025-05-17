# Semantic Operating System (Semantic OS)

## Documentation

### Table of Contents
1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Setup Instructions](#setup-instructions)
4. [Usage Guide](#usage-guide)
5. [API Reference](#api-reference)
6. [Extensibility Guide](#extensibility-guide)
7. [Development Roadmap](#development-roadmap)

## Introduction

The Semantic Operating System (Semantic OS) is a proof-of-concept system that enables natural language interactions for managing files and executing tasks on a Linux-based system. It integrates content-aware storage, local language model processing, and a conversational interface to create a more intuitive computing experience.

Semantic OS allows users to:
- Find files based on content and context rather than just filenames
- Interact with the system using natural language commands
- Execute complex tasks through conversational interfaces
- Extend functionality through a modular plugin architecture

This documentation provides comprehensive information on the system architecture, setup instructions, usage examples, API references, and extensibility guidelines.

## System Architecture

Semantic OS is built with a modular architecture that follows SOLID principles for maintainability and extensibility. The system consists of four main components:

### 1. Content-Aware Storage (CAS)

The Content-Aware Storage module provides semantic file indexing and retrieval capabilities. It monitors file system changes, extracts content and metadata from files, and maintains a searchable index.

Key components:
- **File Indexer**: Monitors file system changes and triggers content extraction
- **Content Extractors**: Plugin-based system for extracting content from different file types
- **Metadata Store**: Maintains a database of file metadata
- **Semantic Index**: Provides search capabilities using Whoosh
- **CAS API**: Unified interface for interacting with the storage system

### 2. Local Large Language Model (LLM) Integration

The Local LLM Integration module incorporates a lightweight, local language model to interpret and respond to user queries. It facilitates natural language understanding for file operations and task management.

Key components:
- **Model Manager**: Handles model loading, resource management, and optimization
- **Context Manager**: Maintains conversation context and history
- **Prompt Engineer**: Formats inputs for optimal model performance
- **Inference Engine**: Executes model inference with fallback strategies
- **LLM API**: Unified interface for natural language processing

### 3. Natural Language Interface

The Natural Language Interface module provides a terminal-based chat interface for conversational interaction with the system. It handles user input, formats system responses, and manages user sessions.

Key components:
- **Terminal UI**: Implements the visual interface using Textual
- **Input Processor**: Handles user input and command history
- **Response Formatter**: Formats system responses for display
- **Session Manager**: Maintains user session state
- **Interface API**: Unified interface for the terminal interaction

### 4. Modular Command Processing (MCP) and Agent-to-Agent (A2A) Architecture

The MCP and A2A architecture enables extensible command processing and inter-agent communication. It supports a plugin-based system where specialized agents can handle specific tasks or commands.

Key components:
- **Command Router**: Directs requests to appropriate command processors
- **Agent Registry**: Maintains a registry of available agents and capabilities
- **Message Bus**: Facilitates communication between agents
- **Command Processors**: Plugin architecture for processing different commands
- **Workflow Engine**: Orchestrates multi-step workflows
- **MCP API**: Unified interface for command processing and agent communication

### System Integration

The components are integrated through well-defined APIs, allowing for loose coupling and independent development. The system follows a layered architecture:

1. **User Interface Layer**: Natural Language Interface
2. **Processing Layer**: LLM Integration and Modular Command Processing
3. **Storage Layer**: Content-Aware Storage

Communication between layers is handled through the respective APIs, ensuring modularity and maintainability.

## Setup Instructions

### Prerequisites

- Linux-based operating system
- Python 3.10 or higher
- Git (for cloning the repository)
- 4GB+ RAM (8GB recommended for optimal performance)
- 2GB+ free disk space

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/semantic-os.git
   cd semantic-os
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download the language model:
   ```bash
   python scripts/download_model.py
   ```

### Configuration

1. Create a configuration file:
   ```bash
   cp config.example.json config.json
   ```

2. Edit the configuration file to specify:
   - Directories to monitor
   - Language model settings
   - Interface preferences

### Running Semantic OS

1. Start the system:
   ```bash
   python src/main.py
   ```

2. The terminal interface will appear, allowing you to interact with the system using natural language.

## Usage Guide

### Basic Commands

Semantic OS understands a wide range of natural language commands. Here are some examples:

#### File Operations

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

- **Deleting files**:
  ```
  Delete temporary files older than 30 days
  Remove the draft version of my thesis
  ```

#### System Information

- **Getting system status**:
  ```
  Show system information
  What's the status of the semantic index?
  How many files are being monitored?
  ```

- **Help and guidance**:
  ```
  What can you help me with?
  Show available commands
  How do I search for files?
  ```

### Advanced Usage

#### Complex Queries

Semantic OS can handle complex queries that combine multiple operations:

```
Find all Python files related to data analysis and create a summary
Search for documents about climate change and extract key points
Find files I worked on last week and organize them by project
```

#### Workflows

You can create and execute multi-step workflows:

```
Create a workflow to find all research papers, extract their abstracts, and generate a summary
Set up a daily task to organize my downloads folder
```

#### Session Management

Semantic OS maintains conversation context, allowing for follow-up queries:

```
User: Find files about machine learning
System: [Shows results]
User: Which ones were modified this week?
System: [Filters results based on modification time]
```

## API Reference

### Content-Aware Storage API

The CAS API provides methods for indexing, searching, and managing files.

```python
from cas.cas_api import ContentAwareStorage

# Initialize CAS
cas = ContentAwareStorage(
    monitored_directories=['/path/to/monitor'],
    storage_dir='/path/to/storage'
)

# Start monitoring
cas.start()

# Search for files
results = cas.search('python programming')

# Get file metadata
metadata = cas.get_file_metadata('/path/to/file.txt')

# Stop monitoring
cas.stop()
```

### Local LLM API

The LLM API provides methods for natural language processing.

```python
from llm.llm_api import LocalLLM

# Initialize LLM
llm = LocalLLM(
    storage_dir='/path/to/storage',
    model_name='microsoft/phi-2'
)

# Initialize the model
llm.initialize(quantize=True)

# Process a query
response = llm.process_query('What is semantic computing?')

# Extract intent
intent = llm.extract_intent('Find files related to Python')

# Shutdown
llm.shutdown()
```

### Natural Language Interface API

The Interface API provides methods for user interaction.

```python
from interface.interface_api import NaturalLanguageInterface

# Initialize interface
interface = NaturalLanguageInterface(
    storage_dir='/path/to/storage',
    message_handler=handle_message
)

# Define message handler
def handle_message(message):
    # Process message
    return "Response to user"

# Start interface
interface.start()

# Display messages
interface.display_assistant_message('This is a response')
interface.display_system_message('System notification')

# Stop interface
interface.stop()
```

### Modular Command Processing API

The MCP API provides methods for command processing and agent communication.

```python
from mcp.mcp_api import ModularCommandProcessing

# Initialize MCP
mcp = ModularCommandProcessing(
    storage_dir='/path/to/storage',
    llm_service=llm,
    cas_service=cas
)

# Register an agent
mcp.register_agent(
    'custom_agent',
    {
        'name': 'Custom Agent',
        'version': '0.1.0',
        'description': 'Custom agent for specific tasks',
        'capabilities': ['custom_capability']
    }
)

# Process a command
result = mcp.process_command('Find files about Python')

# Create a workflow
workflow_id = mcp.create_workflow(
    name='File Processing Workflow',
    description='Process files in multiple steps'
)

# Add workflow steps
step_id = mcp.add_workflow_step(
    workflow_id=workflow_id,
    agent_id='search_processor',
    action='search_files',
    parameters={'query': 'Python'}
)

# Start workflow
mcp.start_workflow(workflow_id)
```

## Extensibility Guide

Semantic OS is designed to be extensible through a plugin architecture. This section explains how to extend the system with custom functionality.

### Adding Content Extractors

Content extractors allow the system to understand new file types.

1. Create a new extractor class:

```python
from cas.extractors import BaseExtractor

class CustomFormatExtractor(BaseExtractor):
    """Extractor for custom file format."""
    
    def can_extract(self, file_path):
        """Check if this extractor can handle the file."""
        return file_path.endswith('.custom')
    
    def extract_content(self, file_path):
        """Extract content from the file."""
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Process content
        processed_content = self._process_custom_format(content)
        
        return {
            'text': processed_content,
            'metadata': {
                'format': 'custom',
                'version': self._detect_version(content)
            }
        }
    
    def _process_custom_format(self, content):
        # Custom processing logic
        return content
    
    def _detect_version(self, content):
        # Version detection logic
        return '1.0'
```

2. Register the extractor:

```python
from cas.cas_api import ContentAwareStorage
from custom_extractors import CustomFormatExtractor

# Initialize CAS
cas = ContentAwareStorage(
    monitored_directories=['/path/to/monitor'],
    storage_dir='/path/to/storage'
)

# Register custom extractor
cas.register_extractor(CustomFormatExtractor())

# Start monitoring
cas.start()
```

### Adding Command Processors

Command processors allow the system to handle new types of commands.

1. Create a new processor class:

```python
from mcp.command_processor import BaseCommandProcessor

class CustomCommandProcessor(BaseCommandProcessor):
    """Processor for custom commands."""
    
    def __init__(self):
        """Initialize the processor."""
        super().__init__()
        self.update_metadata({
            'name': 'CustomCommandProcessor',
            'description': 'Handles custom commands',
            'capabilities': ['custom_command']
        })
    
    def can_process(self, intent):
        """Check if this processor can handle the intent."""
        return intent == 'custom_command'
    
    def process(self, command, intent_data, context):
        """Process a command."""
        # Custom processing logic
        return {
            'status': 'success',
            'message': 'Custom command processed',
            'operation': 'custom_command',
            'result': 'Custom result'
        }
```

2. Register the processor:

```python
from mcp.mcp_api import ModularCommandProcessing
from custom_processors import CustomCommandProcessor

# Initialize MCP
mcp = ModularCommandProcessing(
    storage_dir='/path/to/storage',
    llm_service=llm,
    cas_service=cas
)

# Create processor instance
custom_processor = CustomCommandProcessor()

# Register processor
mcp.register_command_processor('custom_command', custom_processor.process)

# Register agent for the processor
mcp.register_agent(
    'custom_processor',
    {
        'name': 'Custom Command Processor',
        'version': '0.1.0',
        'description': 'Handles custom commands',
        'capabilities': ['custom_command']
    }
)
```

### Creating Agents

Agents are autonomous components that can perform specific tasks and communicate with other agents.

1. Create a new agent class:

```python
from mcp.message_bus import Message

class CustomAgent:
    """Custom agent for specific tasks."""
    
    def __init__(self, agent_id, mcp):
        """Initialize the agent."""
        self.agent_id = agent_id
        self.mcp = mcp
        
        # Register with MCP
        self.mcp.register_agent(
            self.agent_id,
            {
                'name': 'Custom Agent',
                'version': '0.1.0',
                'description': 'Agent for custom tasks',
                'capabilities': ['custom_task']
            }
        )
        
        # Subscribe to messages
        self.mcp.subscribe_to_messages(self.agent_id, self._handle_message)
    
    def _handle_message(self, message):
        """Handle incoming messages."""
        content = message.content
        
        if isinstance(content, dict) and content.get('action') == 'custom_task':
            # Process the task
            result = self._process_task(content)
            
            # Send response
            self.mcp.send_message(
                sender=self.agent_id,
                recipients=[message.sender],
                topic='task_result',
                content={
                    'action': 'task_completed',
                    'result': result,
                    'correlation_id': message.correlation_id
                }
            )
    
    def _process_task(self, task_data):
        """Process a custom task."""
        # Custom task processing logic
        return {'status': 'completed', 'data': 'Task result'}
```

2. Initialize and start the agent:

```python
from custom_agents import CustomAgent

# Create agent
custom_agent = CustomAgent('custom_agent_1', mcp)

# Use the agent through MCP
result = mcp.process_command('Perform custom task')
```

## Development Roadmap

Future development of Semantic OS will focus on the following areas:

1. **Enhanced Natural Language Understanding**:
   - Support for more complex queries and commands
   - Improved context awareness and conversation memory
   - Multi-language support

2. **Advanced Content Analysis**:
   - Deep semantic understanding of file contents
   - Relationship mapping between files and concepts
   - Automatic categorization and tagging

3. **User Experience Improvements**:
   - Graphical user interface option
   - Voice interaction capabilities
   - Personalized adaptations based on usage patterns

4. **Performance Optimization**:
   - Faster indexing and search
   - More efficient language model inference
   - Reduced memory footprint

5. **Integration Capabilities**:
   - APIs for third-party application integration
   - Cloud synchronization options
   - Mobile companion applications

## Conclusion

Semantic OS represents a step toward more intuitive and natural computing experiences. By combining content-aware storage, local language model processing, and conversational interfaces, it enables users to interact with their computers in ways that more closely match human thought processes.

This proof-of-concept demonstrates the feasibility and potential of semantic computing paradigms for everyday use. We encourage contributions and extensions to the system to explore new possibilities in human-computer interaction.

---

For support, contributions, or more information, please contact the development team or visit the project repository.
