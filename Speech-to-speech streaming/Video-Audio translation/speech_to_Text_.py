# pip install assemblyai
import assemblyai as aai
import os

# Set API key
aai.settings.api_key = "7e188095c594495d94011a0eebe1c47f"
transcriber = aai.Transcriber()

def transcribe_audio(input_file, output_file):
    """
    Transcribes audio from the input file and saves the transcription to a text file.

    :param input_file: Path to the audio file to be transcribed.
    :param output_file: Path to save the transcription text file.
    """
    # Perform transcription
    transcript = transcriber.transcribe(input_file)

    # Check transcription status and save to a text file
    if transcript.status == aai.TranscriptStatus.error:
        print(f"Transcription error: {transcript.error}")
    else:
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(transcript.text)
        print(f"Transcript saved to {output_file}")

if __name__ == "__main__":
    # Prompt the user for the audio file path
    input_file = input("Enter the path to the audio file to transcribe (e.g., C:/path/to/file.wav): ").strip()
    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' does not exist.")
        exit(1)

    # Prompt the user for the output file path
    output_file = input("Enter the path to save the transcription (e.g., C:/path/to/output.txt): ").strip()
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        print(f"Error: The directory '{output_dir}' does not exist.")
        exit(1)

    # Transcribe the audio and save the text
    transcribe_audio(input_file, output_file)
