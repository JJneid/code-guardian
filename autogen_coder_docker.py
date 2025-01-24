import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from autogen_ext.tools.code_execution import PythonCodeExecutionTool
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.tools import FunctionTool
from autogen_core.code_executor import CodeBlock
from autogen_agentchat.conditions import TextMentionTermination
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

async def main() -> None:
    # Create the Docker code executor with the correct socket location
    docker_executor = DockerCommandLineCodeExecutor(
        work_dir="coding",
        image="python:3-slim",
        timeout=60,
        auto_remove=True
    )
    
    # Set Docker socket location for macOS
    os.environ['DOCKER_HOST'] = 'unix:///Users/JJneid/.docker/run/docker.sock'
    
    # Start the executor
    await docker_executor.start()
    
    try:
        # Create the Python execution tool with Docker executor
        tool = PythonCodeExecutionTool(docker_executor)
        
        agent = AssistantAgent(
            "assistant", 
            OpenAIChatCompletionClient(model="gpt-4o-mini"), 
            tools=[tool], 
            reflect_on_tool_use=True, 
            system_message="""
            generate one code block for the task and execute it. install dependencies within the code, use the following format tp handle each package depency 
            import subprocess
subprocess.check_call(['pip', 'install', 'package_name'])
"""
        )

        result = await Console(
            agent.run_stream(
                task="Analyze American Airlines (AAL) stock, include last 2 years, use scikit learn"
            )
        )
        print(result.messages[-1].content)
        
    finally:
        # Make sure to stop the Docker executor
        await docker_executor.stop()

asyncio.run(main())