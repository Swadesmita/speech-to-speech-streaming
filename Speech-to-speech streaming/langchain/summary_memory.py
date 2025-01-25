from langchain.chains.conversation.memory import ConversationSummaryBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAl
from langchain.chains import ConversationChain

#Initialize the chat model

llm = ChatGoogleGenerativeAl(model = "gemini-1.5-flag")

#It creates a sumary buffer nemory that keeps a summary of old nessages and recent messages in buffer

memory = ConversationSummaryBufferMemory(
    llm = llm,
    max_token_Limit=200, #Maximun number of tokens to keep in memory
)

#It creates a conversation chain with the chat model and summary buffer nemory
conversation = ConversationChain(
    llm = llm,
    memory = memory,
    verbose = True #To see the conversation flow
)

while True:
#Here we are taking user input
    user_input = input("\nYou: ")

#Check for exit command
    if user_input.lower() in ['bye','exit']:
        print("Goodbye!")
        
        #Print the conversation history with sumaries
        print("\nConversation Summary:")
        print(conversation.memory.buffer)
        break

#Here we are getting the response from the Al 
response = conversation.predict(input= user_input)
print("\n", response)
