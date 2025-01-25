from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
memory = ConversationBufferMemory()
llm = ChatGoogleGenerativeAI(model = "gemini-1.5-flash")
conversation = ConversationChain(
    llm=llm,
    memory= memory,
)

while true:
    user_input = input("\nYou: ")
    if user_input.lower() in ['bye','exit']:
        print("Goodbye!")
    
        print(conversation.memory.buffer)
        break
    
    response = conversation.predict(input= user_input)
    print("\nAI:", response)