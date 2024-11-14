from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from dotenv import load_dotenv
import os
load_dotenv()
import json

class BotPlugin:
    def init(self):
        self.kernel = Kernel()
        self.userIntentRequestResponse=None

        azure_chat_service = AzureChatCompletion(
                service_id="bot",
                deployment_name=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
             )

        self.kernel.add_service(azure_chat_service)

        base_plugin = "C:/Users/rahulkumar.s/PwC_Flexa_Chatbot/health_care/"        

        semantic_plugin = self.kernel.add_plugin(parent_directory=base_plugin, plugin_name="Plugins")

        self.user_intent_function = semantic_plugin["UserIntent"]

        self.bot_response = semantic_plugin["BotResponse"]

    @kernel_function(name ="UserIntentRequest",description="For the input provided return the user intent")
    async def UserIntentRequest(self, user_input: str):
        print("Invoking UserIntentRequest")

        userIntentResponse = await self.kernel.invoke(self.user_intent_function, KernelArguments(input=user_input))
        print(userIntentResponse)

        #self.userIntentRequestResponse = str(userIntentResponse)
        self.userIntentRequestResponse = json.loads(str(userIntentResponse))        

    @kernel_function(name="BotDecisionManagement", description="return the response from this function")
    async def BotDecisionManagement(self):
        print("Invoking BotResponseManagement")

        UserIntent = self.userIntentRequestResponse.get("UserIntent")
        response = await self.kernel.invoke(self.bot_response, KernelArguments(input=UserIntent))

        print(response)        

        return response