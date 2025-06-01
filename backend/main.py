from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import re
import time
import json
import pandas as pd
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="YouTube Deep Insights API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class VideoAnalysisRequest(BaseModel):
    video_url: str
    model_name: str
    mode: str  # 'Comments Only', 'Transcript Only', or 'Both'

class AnalysisResponse(BaseModel):
    video_title: str
    transcript: Optional[str]
    comments: List[str]
    analysis: str

# Configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CACHE_DIR = "cache"

os.makedirs(CACHE_DIR, exist_ok=True)

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

model_map = {
    "LLama-Nvidia": "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
    "Google Gemini": "google/gemini-2.5-pro-exp-03-25:free",
    "Google Gemma": "google/gemma-3-12b-it:free",
    "Meta Maverick": "meta-llama/llama-4-maverick:free",
    "GPT 4.1 Nano": "openai/gpt-4.1-nano",
    "Grok": "x-ai/grok-3-mini-beta",
    "DeepSeek": "deepseek/deepseek-chat-v3-0324",
}

def extract_video_id(url: str) -> Optional[str]:
    match = re.search(r"(?:v=|/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def get_video_title(video_id: str) -> str:
    try:
        resp = youtube.videos().list(part="snippet", id=video_id).execute()
        if resp.get("items"):
            return re.sub(r'[\\/*?:"<>|]', "_", resp["items"][0]["snippet"]["title"])
    except Exception as e:
        return "Untitled"
    return "Untitled"

def get_comments(video_id: str) -> List[str]:
    path = os.path.join(CACHE_DIR, f"comments_{video_id}.json")
    if os.path.exists(path):
        return pd.read_json(path)["comment"].tolist()
    comments = []
    seen = set()
    token = None
    try:
        while True:
            resp = youtube.commentThreads().list(
                part="snippet", videoId=video_id, maxResults=100, pageToken=token, textFormat="plainText"
            ).execute()
            for item in resp.get("items", []):
                txt = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"].strip()
                if txt and txt not in seen:
                    comments.append(txt)
                    seen.add(txt)
                    if len(comments) >= 3000:
                        break
            token = resp.get("nextPageToken")
            if not token or len(comments) >= 3000:
                break
            time.sleep(0.1)
        pd.DataFrame({"comment": comments}).to_json(path, orient="records")
        return comments
    except Exception as e:
        return []

def get_transcript(video_id: str, retries: int = 3, delay: int = 2) -> Optional[str]:
    path = os.path.join(CACHE_DIR, f"transcript_{video_id}.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    attempt = 0
    while attempt < retries:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            result = " ".join([entry['text'] for entry in transcript])
            with open(path, "w", encoding="utf-8") as f:
                f.write(result)
            return result
        except (TranscriptsDisabled, NoTranscriptFound):
            return None
        except Exception as e:
            attempt += 1
            time.sleep(delay * (2 ** attempt))
    return None

def call_openrouter(prompt: str, model_name: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "DidiBeing",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        if res.status_code != 200:
            return ""
        result = res.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        return ""
    except Exception as e:
        return ""

@app.get("/api/models")
def get_available_models():
    return list(model_map.keys())

@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze_video(request: VideoAnalysisRequest):
    video_id = extract_video_id(request.video_url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    video_title = get_video_title(video_id)
    transcript = get_transcript(video_id) if request.mode in ("Transcript Only", "Both") else None
    comments = get_comments(video_id) if request.mode in ("Comments Only", "Both") else []
    # Compose prompt for AI analysis
    prompt = f"Analyze the following YouTube video. Title: {video_title}\n\n"
    if transcript:
        prompt += f"Transcript:\n{transcript}\n\n"
    if comments:
        prompt += f"Comments:\n{json.dumps(comments[:100], indent=2)}\n\n"
    prompt += "Please provide a detailed psychological analysis of the video content and audience reactions."
    analysis = call_openrouter(prompt, model_map[request.model_name])
    return AnalysisResponse(
        video_title=video_title,
        transcript=transcript,
        comments=comments,
        analysis=analysis
    ) 