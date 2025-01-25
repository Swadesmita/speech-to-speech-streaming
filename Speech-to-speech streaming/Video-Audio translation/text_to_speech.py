from gtts import gTTS
from pydub import AudioSegment
import os

def text_to_speech(input_file, output_file, language_code="hi", target_duration=None):
    """
    Converts text to speech, adjusts timing if needed, and saves it as an audio file.

    :param input_file: Path to the file containing the text to convert to speech.
    :param output_file: Path to save the generated audio file.
    :param language_code: Language code for TTS (default is "hi" for Hindi).
    :param target_duration: Target duration for the audio in milliseconds (optional).
    """
    # Read the translated text
    with open(input_file, "r", encoding="utf-8") as file:
        text = file.read()

    # Generate speech
    tts = gTTS(text=text, lang=language_code, slow=False)
    temp_audio_file = "temp_audio.mp3"
    tts.save(temp_audio_file)
    print("Generated audio file:", temp_audio_file)

    # Adjust timing if target_duration is provided
    if target_duration:
        # Load the generated audio
        audio = AudioSegment.from_mp3(temp_audio_file)
        current_duration = len(audio)
        
        # Stretch or compress audio to match the target duration
        if current_duration != target_duration:
            speed_factor = current_duration / target_duration
            adjusted_audio = audio.speedup(playback_speed=speed_factor)
            adjusted_audio.export(output_file, format="mp3")
            print(f"Adjusted audio saved to {output_file} with duration: {target_duration}ms")
        else:
            # Save without adjustments if durations match
            audio.export(output_file, format="mp3")
            print(f"Audio duration already matches target duration. Saved to {output_file}.")
    else:
        # Save without adjustments if no target duration is specified
        os.rename(temp_audio_file, output_file)
        print(f"Audio saved to {output_file}")

    # Clean up temporary files
    if os.path.exists(temp_audio_file):
        os.remove(temp_audio_file)

if __name__ == "__main__":
    # Prompt the user for input file path
    translated_text_file = input("Enter the path to the text file to convert to audio (e.g., C:/path/to/file.txt): ").strip()
    if not os.path.exists(translated_text_file):
        print(f"Error: The file '{translated_text_file}' does not exist.")
        exit(1)

    # Prompt the user for output file path
    speech_output_file = input("Enter the path to save the output audio file (e.g., C:/path/to/output.mp3): ").strip()
    output_dir = os.path.dirname(speech_output_file)
    if output_dir and not os.path.exists(output_dir):
        print(f"Error: The directory '{output_dir}' does not exist.")
        exit(1)

    # Prompt the user to confirm or change the language code
    print("Enter the language code for text-to-speech (e.g., 'hi' for Hindi, 'en' for English, etc.):")
    language_code = input("Language code: ").strip().lower()

    # Convert 'hindi' to 'hi' if the user enters 'hindi'
    if language_code == "hindi":
        language_code = "hi"

    # Prompt the user for the target audio duration (in seconds)
    target_duration_sec = input("Enter target audio duration in seconds (or press Enter to skip): ").strip()
    target_duration_ms = int(float(target_duration_sec) * 1000) if target_duration_sec else None

    # Generate and adjust the audio
    text_to_speech(translated_text_file, speech_output_file, language_code, target_duration_ms)
