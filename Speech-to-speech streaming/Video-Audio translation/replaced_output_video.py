import ffmpeg

def replace_audio_in_video():
    # Prompt the user for the video file
    video_file = input("Enter the path to the video file (e.g., C:/path/to/video.mp4): ").strip()
    # Validate the video file path
    if not video_file or not video_file.endswith(('.mp4', '.mkv', '.avi')):
        print("Invalid video file path or format. Please provide a valid video file.")
        return

    # Prompt the user for the audio file
    audio_file = input("Enter the path to the audio file (e.g., C:/path/to/audio.mp3): ").strip()
    # Validate the audio file path
    if not audio_file or not audio_file.endswith(('.mp3', '.aac', '.wav')):
        print("Invalid audio file path or format. Please provide a valid audio file.")
        return

    # Prompt the user for the output file name
    output_file = input("Enter the desired name for the output file (including the path and extension): ").strip()
    # Validate the output file path
    if not output_file or not output_file.endswith(('.mp4', '.mkv', '.avi')):
        print("Invalid output file format. Please provide a valid output file name with extension.")
        return

    try:
        # Input the video and audio streams
        video_stream = ffmpeg.input(video_file)
        audio_stream = ffmpeg.input(audio_file)

        # Process the video with the new audio
        print(f"Processing... The output will be saved to: {output_file}")
        ffmpeg.output(
            video_stream.video,
            audio_stream.audio,
            output_file,
            vcodec='copy',
            acodec='aac'
        ).run()
        print(f"Audio successfully replaced! Output saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("Welcome to the Video-Audio Replacer!")
    replace_audio_in_video()

