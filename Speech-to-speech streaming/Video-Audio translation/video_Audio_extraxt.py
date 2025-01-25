import subprocess
import os

def extract_audio(video_path, audio_path):
    """
    Extracts audio from the video file using FFmpeg.
    """
    # Ensure audio_path has a proper file name (e.g., 'output.wav')
    if not audio_path.endswith(".wav"):
        audio_path += ".wav"
    
    # Make sure the video path does not contain extra quotes
    video_path = video_path.strip('"')
    
    command = [
        "ffmpeg",
        "-i", video_path,  # Input video file
        "-vn",              # No video output
        "-acodec", "pcm_s16le",  # Audio codec
        "-ar", "44100",     # Sample rate
        "-ac", "2",         # Channels (stereo)
        audio_path          # Output audio file
    ]
    
    subprocess.run(command, check=True)

if __name__ == "__main__":
    video_path = input("Enter the path to the video file: ")
    audio_path = input("Enter the path to save the extracted audio (e.g., output.wav): ")
    extract_audio(video_path, audio_path)
    print(f"Audio extracted successfully and saved to {audio_path}.")
