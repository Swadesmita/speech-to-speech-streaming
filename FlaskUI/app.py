import os
import subprocess
import time
import re
from flask import Flask, render_template, request, jsonify, send_from_directory, Response, url_for
from werkzeug.utils import secure_filename
import ffmpeg
import assemblyai as aai
from gtts import gTTS  # Import gTTS
import uuid
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path="C:/coding/python/INFOSYS/FlaskUI/.env")
api_key = os.getenv("API_KEY")
aai_api_key = os.getenv("ASSEMBLYAI_API_KEY")
print(aai_api_key)
print(f"AssemblyAI API Key loaded: {aai_api_key}")  # Debug print

# Define upload folder under FlaskUI folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), "FlaskUI", "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv'}

SUPPORTED_LANGUAGES = {
    'hi': 'Hindi',
    'od': 'Odia',
    'en': 'English',
    'fr': 'French',
    'de': 'German',
    'ta': 'Tamil',
    'te': 'Telugu',
    'mr': 'Marathi',
    'kn': 'Kannada',
    'gu': 'Gujarati',
    'pa': 'Punjabi',
}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
print(f"UPLOAD_FOLDER is set to: {app.config['UPLOAD_FOLDER']}")



# Helper function to validate file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Extract audio from video
def extract_audio(video_path, audio_path, progress_callback):
    ffmpeg_path = "C:\coding\python\INFOSYS\ffmpeg"
    command = [
        "ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le",
        "-ar", "44100", "-ac", "2", audio_path
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE , universal_newlines=True)
    total_duration = None
    for line in process.stderr:
        if line in process.stderr:
            if isinstance(line , bytes):
                line = line.decode('utf-8')
                
        if not total_duration:
            match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', line)
            if match:
                hours, minutes, seconds = map(float, match.groups())
                total_duration = hours * 3600 + minutes * 60 + seconds
                
        match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
        if match and total_duration:
            hours, minutes, seconds = map(float, match.groups())
            elapsed_time = hours * 3600 + minutes * 60 + seconds
            progress = (elapsed_time / total_duration) * 100
            progress_callback(progress)
            
    process.wait()
    if process.returncode != 0:
        raise Exception("FFmpeg command failed")

def parse_ffmpeg_progress(line):
    # Example: frame=  2450 fps= 33 q=28.0 Lsize=    5248kB time=00:01:45.09 bitrate= 407.5kbits/s
    match = re.search(r'time=(\d+:\d+:\d+\.\d+)', line.decode('utf-8'))
    if match:
        time_str = match.group(1)
        minutes, seconds = time_str.split(":")[1:]
        return int(minutes) * 60 + float(seconds)
    return 0

# Transcribe audio using AssemblyAI
def transcribe_audio(audio_path):
    aai.api_key = aai_api_key  # Ensure API key is assigned here
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_path)
    if transcript.status == aai.TranscriptStatus.error:
        raise Exception(f"Transcription failed: {transcript.error}")
    return transcript.text


# Translate text using LangChain with Google GenAI
def translate_text(text, target_language):
    prompt_template = """Translate the following text into {language}: {sentence}"""
    prompt = PromptTemplate(input_variables=["sentence", "language"], template=prompt_template)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=api_key)
    chain = prompt | llm | StrOutputParser()
    try:
        translated_text = chain.invoke({"sentence": text, "language": target_language})
        return translated_text
    except Exception as e:
        raise Exception(f"Error with Google Generative API: {str(e)}")


# Convert text to speech using gTTS
def text_to_speech(text, output_file, language_code):
    tts = gTTS(text=text, lang=language_code, slow=False)
    tts.save(output_file)

# Replace audio in video
def replace_audio_in_video(video_path, audio_path, output_path):
    video_stream = ffmpeg.input(video_path)
    audio_stream = ffmpeg.input(audio_path)
    ffmpeg.output(video_stream.video, audio_stream.audio, output_path, vcodec="copy", acodec="aac", 
                  strict="experimental", af='silenceremove=start_periods=1:start_duration=1:start_threshold=-50dB').run()
# Progress callback
def send_progress(progress):
    print(f"Progress: {progress}%")

# Stream progress updates to frontend using SSE
@app.route("/progress")
def progress():
    def generate():
        while True:
            if 'current_progress' in app.config:
                progress = app.config['current_progress']
                yield f"data: {progress}\n\n"
                if progress >= 100:
                    break
            time.sleep(1)  # Check progress every second

    return Response(generate(), content_type='text/event-stream')

def send_progress(progress):
    app.config['current_progress'] = round(progress)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Handle file upload
        video_file = request.files.get("video")
        if not video_file or video_file.filename == "":
            return jsonify({"error": "No file uploaded"}), 400
        if not allowed_file(video_file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        language = request.form.get("language")
        if not language or language not in SUPPORTED_LANGUAGES:
            return jsonify({"error": "Invalid or no language selected. Supported languages are: " + ", ".join(SUPPORTED_LANGUAGES)}), 400

        # Save uploaded video inside the 'FlaskUI/uploads' folder
        unique_id = uuid.uuid4().hex
        video_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{unique_id}_{secure_filename(video_file.filename)}")
        
        try:
            # Save file and handle errors
            video_file.save(video_path)
            app.logger.info(f"File saved to {video_path}")
        except Exception as e:
            app.logger.error(f"Failed to save the video file: {str(e)}")
            return jsonify({"error": f"Failed to save the file: {str(e)}"}), 500

        try:
            # Process video
            audio_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{unique_id}.wav")
            extract_audio(video_path, audio_path, progress_callback=send_progress)

            transcript = transcribe_audio(audio_path)
            translated_text = translate_text(transcript, language)

            speech_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{unique_id}_{language}.mp3")
            text_to_speech(translated_text, speech_path, language)

            output_video_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{unique_id}_translated_{language}.mp4")
            replace_audio_in_video(video_path, speech_path, output_video_path)

            return jsonify({
                "message": "Video processed successfully",
                "download_link": url_for('uploaded_file', filename=f"{unique_id}_translated_{language}.mp4", _external=True),
                "original_video_url": url_for('uploaded_file', filename=f"{unique_id}_{secure_filename(video_file.filename)}", _external=True),
                "translated_video_url": url_for('uploaded_file', filename=f"{unique_id}_translated_{language}.mp4", _external=True)
            })

        except Exception as e:
            app.logger.error(f"Error during video processing: {str(e)}")
            return jsonify({"error": f"Error processing the video: {str(e)}"}), 500

    return render_template("index.html")


@app.route('/uploaded_file/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
    app.run(debug=True)