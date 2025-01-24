# Safe Code Execution Agent

This guide explains how to build an AI agent that can safely execute code in an isolated Docker environment.

## Prerequisites

- Python 3.8+
- Docker installed and running
- OpenAI API key

## Installation

```bash
pip install autogen-agentchat autogen-ext python-dotenv
```

## Key Components

### 1. Docker Executor
- Provides isolated environment for code execution
- Prevents harmful code from affecting host system
- Auto-removes containers after execution

### 2. Agent Configuration
- Uses OpenAI's GPT models for code generation
- Includes safety measures and execution constraints
- Handles dependency management within container

## Setup Instructions

1. Create `.env` file:
```
OPENAI_API_KEY=your_key_here
```

2. Setup Docker socket:
- Linux: `/var/run/docker.sock`
- macOS: `/Users/username/.docker/run/docker.sock`
- Windows: Use Docker Desktop WSL 2 backend

## Basic Implementation

```python
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_ext.tools.code_execution import PythonCodeExecutionTool

async def create_safe_agent():
    # Initialize Docker executor
    docker_executor = DockerCommandLineCodeExecutor(
        work_dir="coding",
        image="python:3-slim",
        timeout=60,
        auto_remove=True
    )
    
    # Create Python execution tool
    tool = PythonCodeExecutionTool(docker_executor)
    
    # Create agent with safety constraints
    agent = AssistantAgent(
        "assistant",
        OpenAIChatCompletionClient(model="gpt-4"),
        tools=[tool],
        system_message="""
        Generate single code blocks with integrated dependency management.
        Install packages using:
        import subprocess
        subprocess.check_call(['pip', 'install', 'package_name'])
        """
    )
    
    return agent, docker_executor

# Usage example in async context
async def main():
    agent, executor = await create_safe_agent()
    try:
        result = await agent.run("Your task here")
        print(result)
    finally:
        await executor.stop()
```

## Safety Features

1. Isolation
   - Code runs in disposable containers
   - No access to host system
   - Limited resources and timeout

2. Dependency Management
   - Dependencies installed within container
   - Clean environment for each execution
   - Automatic cleanup

3. Error Handling
   - Graceful handling of execution errors
   - Container auto-removal on completion
   - Timeout protection

## Best Practices

1. Always use `try-finally` to ensure executor cleanup
2. Set appropriate timeouts for tasks
3. Validate code before execution when possible
4. Monitor resource usage
5. Keep Docker images updated

## Error Handling

```python
try:
    result = await agent.run(task)
except Exception as e:
    print(f"Execution error: {e}")
finally:
    await executor.stop()
```

## Limitations

- Docker required on host system
- Network access needed for dependencies
- Resource consumption based on container limits

## Security Considerations

- Configure Docker with minimal privileges
- Use slim base images
- Implement additional code validation if needed
- Monitor container resource usage