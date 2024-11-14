import asyncio
import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings
from semantic_kernel.core_plugins.text_plugin import TextPlugin
from semantic_kernel.functions.kernel_function_from_prompt import KernelFunctionFromPrompt
from semantic_kernel.planners import SequentialPlanner
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Kernel and add services
kernel = Kernel()
kernel.add_service(
    AzureChatCompletion(
        service_id="test",
        deployment_name=os.getenv("AZURE_OPENAI_TEXT_DEPLOYMENT_NAME"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2023-05-15",
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
)

# Load plugins
plugins_directory = "C:/Users/rahulkumar.s/PwC_Flexa_Chatbot/health_care"
kernel.add_plugin(plugin_name="Plugins", parent_directory=plugins_directory)
kernel.add_plugin(plugin=TextPlugin(), plugin_name="TextPlugin")

# Define kernel function
flexa_func = KernelFunctionFromPrompt(
    function_name="Bot",
    plugin_name="Plugins",
    prompt="""
{$Input}
{user_input}
""",
    prompt_execution_settings=AzureChatPromptExecutionSettings(
        service_id="test",
        max_tokens=2000,
        temperature=0.5,
    ),
    description="Evaluate contract rules based on engagement territory and type of budget.",
)
kernel.add_function(plugin_name="Plugins", function=flexa_func)

async def create_and_execute_plan(user_input):
    # Create the sequential plan
    planner = SequentialPlanner(kernel, service_id="test")
    sequential_plan = await planner.create_plan(goal=user_input)

    # Print the plan's steps
    print("The plan's steps are:")
    for step in sequential_plan._steps:
        print(
            f"- {step.description.replace('.', '') if step.description else 'No description'} using {step.metadata.fully_qualified_name} with parameters: {step.parameters}"
        )

    # Execute the plan and get the result
    result = await sequential_plan.invoke(kernel)
    return result

# Example usage
user_input = "i want to quit smoking"
result = create_and_execute_plan(user_input)
print(result)