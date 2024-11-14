import asyncio
import logging
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import AzureChatPromptExecutionSettings
from semantic_kernel.contents import ChatHistory
from plugin import BotPlugin
from dotenv import load_dotenv
import os
load_dotenv()

system_message = """
You are an advanced AI chatbot that assists users. 
Your task is to process user input to extract information and invoke the relevant function.
### Instructions

Whenever there is an input, call the UserIntentRequest function. Always invoke this function after every user input.

After invoking the UserIntentRequest function, call the BotDecisionManagement function internally.

Return the response from the BotDecisionManagement function.
"""

kernel = Kernel()
service_id = "testingbot"

azure_chat_service = AzureChatCompletion(
 service_id=service_id,
 deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
 api_key=os.getenv("AZURE_OPENAI_API_KEY"),
 api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
 endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

kernel.add_service(azure_chat_service)

kernel.add_plugin(BotPlugin(), plugin_name="BotPlugin") 

chat_function = kernel.add_function(
 prompt=system_message + """{{$chat_history}}{{$user_input}}""",
 function_name="chat",
 plugin_name="chat",
 prompt_execution_settings=AzureChatPromptExecutionSettings(service_id=service_id,
                                                            function_choice_behavior=FunctionChoiceBehavior.Auto(auto_invoke=True),
                                                            temperature=0.2,
                                                            top_p=0.3,
                                                            max_tokens=2000)
)

history = ChatHistory()
history.add_system_message(system_message)

async def chat() -> bool:
    global history

    try:
        user_input = input("User:> ")

    except (KeyboardInterrupt, EOFError):
        print("\n\nExiting chat...")
        return False

    if user_input.lower() == "exit":
        print("\n\nExiting chat...")
        return False

    history.add_user_message(user_input)

    stream = True
    if stream:
        answer = kernel.invoke_stream(
            chat_function,
            user_input=user_input,
            chat_history=history,
        )
        print(type(answer))
        print("Bot:> ", end="")
        full_response = ""
        async for message in answer:
            full_response += str(message[0])
            print(message[0], end="")
        print("\n")

    # else:
    #     print("else")
    #     answer = await kernel.invoke(
    #         chat_function,
    #         user_input=user_input,
    #         chat_history=history,
    #     )
    #     print(f"Bot:> {answer}")
    #     full_response = str(answer)

    history.add_assistant_message(full_response)
    #print(f"Bot> {full_response}")
    return True

async def main() -> None:
    Bot = "Bot:> Hello! How can i assist you today"
    print(Bot)
    chatting = True
    while chatting:
        chatting = await chat()

if name == "main":

    asyncio.run(main())