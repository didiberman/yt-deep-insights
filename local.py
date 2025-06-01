import os
import re
import time
import json
import pandas as pd
import streamlit as st
import markdown
import requests
from datetime import datetime
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import io
import zipfile
st.set_page_config(
    page_title="AI Psych Research Assistant",
    page_icon="🍍",  # or use "favicon.png" if you have a custom file
)
# Add password protection
if "password_entered" not in st.session_state:
    st.session_state.password_entered = False

if not st.session_state.password_entered:
    st.title("🍍 AI Psychological Research Assistant")
    st.write("Please enter the password")
    password_input = st.text_input("Password:", type="password")
    if st.button("Submit Password"):
        if password_input == "4321":
            st.session_state.password_entered = True
            st.success("Password correct! Please wait...")
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")
    st.stop()

# ---------------------- CONFIG ----------------------
# ---------------------- CONFIG ----------------------
YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY")
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY")
CLAUDE_API_KEY = st.secrets.get("OPENROUTER_API_KEY")
PROXY_URL = "http://didibeing-rotate:ex7s65d96p41@p.webshare.io:80"
# ✅ Full final version with ZIP download

COST_FILE = "total_cost.txt"
CACHE_DIR = "cache"

# Ensure CACHE_DIR exists
os.makedirs(CACHE_DIR, exist_ok=True)



if not YOUTUBE_API_KEY or not OPENROUTER_API_KEY:
    st.error("Missing required API keys in Streamlit secrets.")
    st.stop()

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# ---------------------- COST TRACKING ----------------------
def load_total_cost():
    try:
        with open(COST_FILE, "r") as f:
            return float(f.read().strip())
    except:
        return 0.0

def update_total_cost(amount):
    total = load_total_cost() + amount
    with open(COST_FILE, "w") as f:
        f.write(f"{total:.4f}")
    return total


# ---------------------- MODEL MAPPING ----------------------
model_map = {
    "Optimus-Alpha": "openrouter/optimus-alpha",
    "LLama-Nvidia": "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
    "Google Gemini": "google/gemini-2.5-pro-exp-03-25:free",
    "Google Gemma": "google/gemma-3-12b-it:free",
    "GPT 4o mini": "openai/gpt-4o-mini",
    "Meta Maverick": "meta-llama/llama-4-maverick:free",
    "Grok": "x-ai/grok-3-mini-beta",
    "DeepSeek": "deepseek/deepseek-chat-v3-0324",
}

rates = {
    "Meta Maverick": (0.00, 0.00),
    "Grok": (0.00, 0.00),
    "Optimus-Alpha": (0.0, 0.0),
    "GPT 4o mini": (0.0, 0.0),
    "Google Gemma": (0.0, 0.0),
    "Google Gemini": (0.00, 0.00),
    "DeepSeek": (0.10, 0.30),
    "LLama-Nvidia": (0.0, 0.0)
}

# ---------------------- UTILITIES ----------------------
def extract_video_id(url):
    match = re.search(r"(?:v=|/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

def get_video_title(video_id):
    try:
        resp = youtube.videos().list(part="snippet", id=video_id).execute()
        if resp.get("items"):
            return re.sub(r'[\\/*?:"<>|]', "_", resp["items"][0]["snippet"]["title"])
    except Exception as e:
        st.warning(f"Error fetching title: {e}")
    return "Untitled"


def get_comments(video_id):
    path = os.path.join(CACHE_DIR, f"comments_{video_id}.json")
    if os.path.exists(path):
        st.info("🔁 Using cached comments.")
        return pd.read_json(path)["comment"].tolist()

    comments = []
    seen = set()
    token = None
    st.info("📡 Retrieving comments from YouTube API...")
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
        st.success("✅ Comments retrieved and cached.")
        return comments
    except:
        st.error("⚠️ Failed to retrieve comments. They may be disabled or restricted.")
        return []

def get_transcript(video_id, retries=3, delay=2):
    path = os.path.join(CACHE_DIR, f"transcript_{video_id}.txt")

    # ✅ Return cached transcript if available
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            st.info("📡 Transcript cache located...")
            return f.read()

    proxy = st.secrets.get("PROXY_URL")
    proxies = {"https": proxy} if proxy else None

    attempt = 0
    while attempt < retries:
        try:
            st.info(f"📡 Attempt {attempt+1} to retrieve transcript...")
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'], proxies=proxies)

            # ✅ Convert list of text chunks to a single string
            result = " ".join([entry['text'] for entry in transcript])

            with open(path, "w", encoding="utf-8") as f:
                f.write(result)

            st.success("✅ Transcript retrieved and cached.")
            return result  # ✅ Always return string
        except (TranscriptsDisabled, NoTranscriptFound):
            st.error("⚠️ No English transcript available.")
            return None
        except Exception as e:
            st.warning(f"⚠️ Attempt {attempt+1} failed: {e}")
            attempt += 1
            time.sleep(delay * (2 ** attempt))  # Exponential backoff

    st.error("❌ Failed to retrieve transcript after multiple attempts.")
    return None  # ✅ Return None, never a list

def call_openrouter(prompt, model_name):
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
            st.error(f"❌ OpenRouter API error ({res.status_code}): {res.text}")
            return ""

        result = res.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            st.warning(f"⚠️ OpenRouter response malformed: {result}")
            return ""
    except Exception as e:
        st.warning(f"{model_name} API exception: {e}")
        return ""

# ---------------------- CACHE INIT ----------------------
CACHE_ANALYSIS_FILE = os.path.join(CACHE_DIR, "cached_analyses.json")
def load_cached_analysis():
    if os.path.exists(CACHE_ANALYSIS_FILE):
        with open(CACHE_ANALYSIS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cached_analysis(cache_data):
    with open(CACHE_ANALYSIS_FILE, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

cached_analyses = load_cached_analysis()

# ---------------------- UI ----------------------
st.title("AI Psychological Research Assistant 🍍 Deep YouTube Audience & Content Insights")
urls_input = st.text_area("Enter up to 2 YouTube URLs (one per line):")
mode = st.radio("Choose analysis type:", ["Comments Only", "Transcript Only", "Both"])
model_choice = st.selectbox("Choose AI Model:", list(model_map.keys()), index=0)

if st.button("Run Analysis"):
    urls = [u.strip() for u in urls_input.strip().splitlines() if u.strip()][:2]
    if not urls:
        st.warning("Please enter at least one valid YouTube URL.")
        st.stop()

    for url in urls:
        vid = extract_video_id(url)
        if not vid:
            st.warning(f"Invalid URL: {url}")
            continue

        title = get_video_title(vid)
        st.header(f"🎮 {title}")

        comment_key = f"{vid}_comments_{model_choice}"
        transcript_key = f"{vid}_transcript_{model_choice}"

        if mode in ("Comments Only", "Both"):
            st.subheader("💬 Analyzing Comments")
            cmts = get_comments(vid)
            st.info(f"💬 Retrieved {len(cmts)} comments.")
            if comment_key in cached_analyses:
                st.info("🧐 Loaded cached AI comment analysis.")
                st.markdown(markdown.markdown(cached_analyses[comment_key]), unsafe_allow_html=True)
            else:
                with st.spinner(f"Analyzing comments with {model_choice}..."):
                    comment_prompt = (
                    "You are a psychological research assistant with deep expertise in trauma, somatic healing, nervous system regulation, and emotional development, deeply informed by the works of Thomas Hübl, Gabor Maté, and Andrew Huberman. I will provide you with scraped YouTube comments. Your task is to extract the key emotional and psychological challenges expressed by viewers. First, group the comments into 4–8 categories of emotionally meaningful struggles. For each category, provide: a short title (3–6 words), a 1–2 sentence description, 2–3 representative comments, and 3–4 highly clickable YouTube titles (max 53 characters). For each title, include what the video would cover, why it's a content opportunity, and the character count. Only include categories that reflect meaningful emotional pain or insight. Skip generic gratitude unless it reflects healing. Then provide a section of Meta-Level Emotional Themes (e.g., shame, abandonment, fear, disconnection) — each with a title, a short explanation of how it appears across the comments, and optionally 1–2 quotes. Then provide a Nervous System Impact Analysis: do the comments express overwhelm, fear, regulation, or longing for safety? Then provide a Somatic Language Clarity section: what somatic language or body-based expressions are present or missing? Finally, add a Content Gaps & Opportunities section: what content is missing, what emotional needs are still unmet, and what video ideas could serve them? Format using clear headings, bullet points, and spacing for readability. Be emotionally intelligent and concise. Below are the comments:"
                    + "\n".join(cmts)
                )
                st.info(f"🤖 Analysing comments with {model_choice}...")
                result = call_openrouter(comment_prompt, model_map[model_choice])
                if result.strip():
                    cached_analyses[comment_key] = result
                    save_cached_analysis(cached_analyses)
                    st.markdown(markdown.markdown(result), unsafe_allow_html=True)
                else:
                    st.warning("⚠️ AI returned an empty analysis. Nothing was cached.")
                    st.markdown(markdown.markdown(result), unsafe_allow_html=True)

        if mode in ("Transcript Only", "Both"):
            st.subheader("📜 Analyzing Transcript")
            transcript = get_transcript(vid)
            if not transcript or not isinstance(transcript, str):
                st.error("❌ Transcript is missing or invalid.")
                continue  # or `return` depending on your structure
            word_count = len(transcript.split())
            page_estimate = round(word_count / 300)  # assuming 300 words per page
            st.info(f"📄 Transcript contains: ~{word_count} words (~{page_estimate} pages).")
            read_minutes = round(word_count / 200)  # 200 wpm average
            st.info(f"📖 Estimated read time: {read_minutes} minutes")
            if transcript:
                if transcript_key in cached_analyses:
                    st.info("🧐 Loaded cached AI transcript analysis.")
                    st.markdown(markdown.markdown(cached_analyses[transcript_key]), unsafe_allow_html=True)
                else:
                    with st.spinner("Analyzing transcript with {model_choice}..."):
                        transcript_prompt = (
                        "You are a content researcher and psychological research assistant deeply informed by the work of Nir Eyal, Dan Ariely, Gabor Maté, and Thomas Hübl, blending behavioral economics, trauma-informed storytelling, and nervous system regulation. I will provide you with a scraped YouTube transcript. First, analyze the Hook (first 30–60 seconds): what makes it compelling or emotionally activating? What psychological triggers are used (curiosity, fear, urgency, vulnerability)? Then provide a Structure Breakdown: how is the video organized, what are the emotional or narrative arcs, and how does it support viewer retention? Then provide a Therapist Adaptation section: how could a therapist or emotional educator use a similar structure or hook in their healing content? Then provide a Missed Opportunities & Content Gaps section: what was left unsaid or shallow, where could the emotional depth or insight be expanded? Then suggest 3–6 YouTube Titles (max 53 characters each), each with what the video would cover, why it's a content opportunity, and character count. Then provide a Nervous System Resonance analysis: where is the transcript dysregulating or regulating? Does the pacing soothe or overwhelm the viewer? Then a Somatic Language Depth section: is the language embodied or overly cognitive? Does it reference felt sense, breath, or inner safety? Then provide an Identity Messaging section: does this reinforce victimhood, empowerment, fear, or healing? Format the output using bold headings, bullet points, and clarity. Be psychologically sharp and spiritually attuned. Below is the transcript:"
                        + transcript
                    )
                    st.info(f"🤖 Analysing transcript with {model_choice}...")
                    result = call_openrouter(transcript_prompt, model_map[model_choice])
                    if result.strip():
                        cached_analyses[transcript_key] = result
                        save_cached_analysis(cached_analyses)
                        st.markdown(markdown.markdown(result), unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ AI returned an empty analysis. Nothing was cached.")
                        st.markdown(markdown.markdown(result), unsafe_allow_html=True)

    # ✅ Build single ZIP of all session results (cached or fresh)
    if "session_zip_buffer" not in st.session_state:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for url in urls:
                vid = extract_video_id(url)
                if not vid:
                    continue
                title = get_video_title(vid) or "Untitled"

                comments_path = os.path.join(CACHE_DIR, f"comments_{vid}.json")
                if os.path.exists(comments_path):
                    zipf.write(comments_path, arcname=os.path.basename(comments_path))

                transcript_path = os.path.join(CACHE_DIR, f"transcript_{vid}.txt")
                if os.path.exists(transcript_path):
                    zipf.write(transcript_path, arcname=os.path.basename(transcript_path))

                for key, content in cached_analyses.items():
                    if key.startswith(vid):
                        file_name = key + ".md"
                        zipf.writestr(file_name, content)

        zip_buffer.seek(0)
        st.session_state.session_zip_buffer = zip_buffer
        st.session_state.zip_name = f"{title} ANALYSIS.zip"

    if "session_zip_buffer" in st.session_state:
        st.subheader("📦 Download All Results")
        st.download_button(
            label=f"⬇️ Download Full Session ZIP",
            data=st.session_state.session_zip_buffer,
            file_name=st.session_state.zip_name,
            mime="application/zip",
            key="full_session_download"
        )
    # 📄 AI-Only TXT Analysis Download
    ai_text_buffer = io.StringIO()
    combined_title = []

    for url in urls:
        vid = extract_video_id(url)
        if not vid:
            continue
        title = get_video_title(vid) or "Untitled"
        combined_title.append(title)

        # Add comment analysis
        comment_key = f"{vid}_comments_{model_choice}"
        if mode in ("Comments Only", "Both") and comment_key in cached_analyses:
            ai_text_buffer.write(f"===== AI ANALYSIS: COMMENTS for '{title}' =====\n\n")
            ai_text_buffer.write(cached_analyses[comment_key])
            ai_text_buffer.write("\n\n")

        # Add transcript analysis
        transcript_key = f"{vid}_transcript_{model_choice}"
        if mode in ("Transcript Only", "Both") and transcript_key in cached_analyses:
            ai_text_buffer.write(f"===== AI ANALYSIS: TRANSCRIPT for '{title}' =====\n\n")
            ai_text_buffer.write(cached_analyses[transcript_key])
            ai_text_buffer.write("\n\n")

    ai_analysis_txt = ai_text_buffer.getvalue()

    if ai_analysis_txt.strip():
        st.download_button(
            label="📄 Download AI Analysis Only (.txt)",
            data=ai_analysis_txt,
            file_name="AI_Analysis.txt",
            mime="text/plain",
            key="ai_analysis_txt"
        )

    with st.expander("🗞️ View All Cached Resources"):
        st.markdown("### 📄 AI Analyses")
        if cached_analyses:
            for key in sorted(cached_analyses):
                st.markdown(f"- `{key}`")
        else:
            st.write("No cached AI analyses available.")

        st.markdown("### 💬 Cached Comments Files")
        for file in os.listdir(CACHE_DIR):
            if file.startswith("comments_") and file.endswith(".json"):
                st.markdown(f"- `{file}`")

        st.markdown("### 📜 Cached Transcripts")
        for file in os.listdir(CACHE_DIR):
            if file.startswith("transcript_") and file.endswith(".txt"):
                st.markdown(f"- `{file}`")
if st.button("🧹 Reset All Cache"):
    import shutil

    # Delete everything in cache
    shutil.rmtree(CACHE_DIR)
    os.makedirs(CACHE_DIR, exist_ok=True)

    # Clear in-memory cache too
    cached_analyses.clear()
    save_cached_analysis(cached_analyses)

    st.success("🔁 All caches have been cleared: transcripts, comments, and analyses.")
