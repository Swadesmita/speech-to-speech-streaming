from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv(dotenv_path=r"C:\coding\python\INFOSYS\.env")
api_key = os.getenv("API_KEY")

def translate_text(transcribed_text, target_language):
    template = """Translate the following text into {language}: {sentence}"""
    prompt = PromptTemplate(
        input_variables=["sentence", "language"],
        template=template
    )
    
    # Configure the LLM with timeout and retries
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        api_key=api_key,
        timeout=600  # Set timeout to 10 minutes (adjust as needed)
    )

    chain = prompt | llm | StrOutputParser()
    
    # Retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            res = chain.invoke({"sentence": transcribed_text, "language": target_language})
            return res
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise RuntimeError("Max retries reached. Unable to complete the translation.")
    
if __name__ == "__main__":
    # Prompt the user for the file paths
    input_file = input("Enter the path to the transcribed text file (e.g., C:/path/to/Believe_text.txt): ").strip()
    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' does not exist.")
        exit(1)

    output_file = input("Enter the path to save the translated text (e.g., C:/path/to/translated_text2.txt): ").strip()
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        print(f"Error: The directory '{output_dir}' does not exist.")
        exit(1)

    # Read the transcribed text from the file
    with open(input_file, "r", encoding="utf-8") as file:
        transcribed_text = file.read()

    # Prompt the user for the target language
    print("Choose a target language for translation (e.g., Hindi, Odia, French, etc.):")
    target_language = input("Enter the target language: ").strip().lower()

    try:
        # Translate the text to the chosen language
        translated_text = translate_text(transcribed_text, target_language)

        # Save the translated text to the specified output file
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(translated_text)

        print(f"Translated Text: {translated_text}")
        print(f"Translation saved to {output_file}")
    except RuntimeError as e:
        print(f"Translation failed: {e}")
