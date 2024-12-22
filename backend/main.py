from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from moviepy import *
import whisper
from deep_translator import GoogleTranslator
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Mount the frontend directory to serve static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080"],  # Allow requests from your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (e.g., GET, POST)
    allow_headers=["*"],  # Allow all headers
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    try:
        # Save uploaded video file
        video_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(video_path, "wb") as f:
            f.write(await file.read())

        # Extract audio from video
        audio_path = os.path.join(UPLOAD_DIR, "audio.wav")
        try:
            video_clip = VideoFileClip(video_path)
            video_clip.audio.write_audiofile(audio_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error extracting audio: {str(e)}")

        # Transcribe audio using Whisper
        try:
            model = whisper.load_model("base")
            result = model.transcribe(audio_path, language="de")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error transcribing audio: {str(e)}")

        # Translate to English
        try:
            translator = GoogleTranslator(source="de", target="en")
            translated_subtitles = []
            for segment in result["segments"]:
                start = segment["start"]
                end = segment["end"]
                text = segment["text"]
                translated_text = translator.translate(text)
                translated_subtitles.append(f"{start} --> {end}\n{translated_text}\n")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error translating text: {str(e)}")

        # Save subtitles as SRT
        srt_path = os.path.join(OUTPUT_DIR, "subtitles.srt")
        with open(srt_path, "w") as f:
            f.write("\n".join(translated_subtitles))

        return FileResponse(srt_path, media_type="text/plain", filename="subtitles.srt")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Video Translator API!"}
