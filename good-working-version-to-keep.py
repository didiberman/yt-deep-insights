import os
import re
import time
import pandas as pd
import streamlit as st
import markdown
import requests
from datetime import datetime
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# ---------------------- CONFIG ----------------------
YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY")
OPENROUTER_API_KEY = st.secrets.get("CLAUDE_API_KEY")
COST_FILE = "total_cost.txt"
CACHE_DIR = "cache"

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
    "Quasar": "openrouter/quasar-alpha",
    "LLama-Nvidia": "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
    "Meta": "meta-llama/llama-4-maverick:free",
    "DeepSeek": "deepseek/deepseek-chat-v3-0324",
    "Claude": "anthropic/claude-3-haiku"
}

rates = {
    "Meta": (0.00, 0.00),
    "Quasar": (0.10, 0.30),
    "Claude": (0.25, 1.25),
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

def log_video_usage(video_id, title):
    os.makedirs(CACHE_DIR, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        country = requests.get("https://ipinfo.io/json").json().get("country", "Unknown")
    except:
        country = "Unknown"
    log_line = f"{video_id},{title},{now},{country}\n"
    with open(os.path.join(CACHE_DIR, "usage_log.csv"), "a", encoding="utf-8") as f:
        f.write(log_line)

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

def get_transcript(video_id):
    path = os.path.join(CACHE_DIR, f"transcript_{video_id}.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
                    return f.read()
    try:
        proxy = st.secrets.get("PROXY_URL")
        proxies = {"https": proxy} if proxy else None
        st.info("📡 Retrieving transcript from YouTube...")
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'], proxies=proxies)
        result = " ".join([entry['text'] for entry in transcript])
        with open(path, "w", encoding="utf-8") as f:
            f.write(result)
            st.success("✅ Transcript retrieved and cached.")
            return result
    except (TranscriptsDisabled, NoTranscriptFound):
        st.error("⚠️ No English transcript available.")
        return None
    except Exception as e:
        st.error(f"⚠️ Transcript could not be retrieved due to restrictions. Error: {e}")
        return None

def call_openrouter(prompt, model_name):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "YouTube Analyzer",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        result = res.json()
        if "choices" in result and result["choices"]:
            return result["choices"][0]["message"]["content"]
        else:
            st.warning(f"{model_name} API error: " + result.get("error", {}).get("message", "Unknown error"))
            return ""
    except Exception as e:
        st.warning(f"{model_name} API exception: {e}")
        return ""

# ---------------------- MAIN UI ----------------------



st.title("AI Psychological Research Assistant 🍍 Deep YouTube Audience & Content Insights")

urls_input = st.text_area("Enter up to 2 (!) YouTube URLs (one per line):")
mode = st.radio("Choose analysis type:", ["Comments Only", "Transcript Only", "Both"])
model_choice = st.selectbox("Choose AI Model:", list(model_map.keys()), index=0)


if st.button("Run Analysis"):
    total_session_cost = 0.0
    total_session_cost = 0.0
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
        log_video_usage(vid, title)
        st.header(f"📺 {title}")

        comments_csv = None
        comment_result = None
        transcript_result = None

        if mode in ("Comments Only", "Both"):
            st.subheader("💬 Analyzing Comments")
            cmts = get_comments(vid)
            st.write(f"➡️ {len(cmts)} comments scraped.")
            comments_csv = pd.DataFrame({"comment": cmts}).to_csv(index=False).encode("utf-8")
            with st.spinner(f"Analyzing comments with {model_choice}..."):
                comment_prompt = (
                    "You are a psychological research assistant. Your task is to read user comments and extract key emotional or psychological challenges. "
                    "Group comments into 4–8 categories. For each category, include: A short category title, A short 1–2 sentence description, "
                    "2–3 representative user comment examples, 2-3 youtube title ideas, up to 56 chars, highly clickable and that create curiosity. "
                    "Only include categories that reflect meaningful emotional experiences. Do NOT include gratitude-only comments unless they hint at deeper pain or healing. Have one last section called Content Gaps and Opportunities. in this section suggest what may be missing out there due to the insights gained by the comments about emotional challenges that still persist. make sure the output i receive from you is properly formatted with highlighted captions, line breaks between each piece"
                    "of data and properly formatted to be easier to digest."
                    "When listing example user comments or suggested YouTube titles, "
                    "use bullet points with a blank line between each item. For example:\n\n"
                    "- Comment #1\n\n"
                    "- Comment #2\n\n"
                    "Make sure you use two newlines (`\\n\\n`) after each bullet. "
                    "Do not merge them into a single paragraph.\n"
                    + "\n".join(cmts)
                )
                comment_result = call_openrouter(comment_prompt, model_map[model_choice])
                prompt_cost = rates[model_choice][0] * len(comment_prompt.split()) / 1000
                total_session_cost += prompt_cost
                prompt_cost = rates[model_choice][0] * len(comment_prompt.split()) / 1000  # estimate input cost
                total_session_cost += prompt_cost
                st.markdown(markdown.markdown(comment_result), unsafe_allow_html=True)

        if mode in ("Transcript Only", "Both"):
            st.subheader("📜 Analyzing Transcript")
            transcript = get_transcript(vid)
            if transcript:
                with st.spinner(f"Analyzing transcript with {model_choice}..."):
                    transcript_prompt = (
                    "You are a youtube content strategist. Analyse why did this video perform well, paying particular attention to the first 30 seconds to 1 minute of the video, as those set the standard for retention. "
                    "Analyse the hook, then the structure of the video itself, the titles for each section, and how I can use this data to inform my own hook as a psychologist therapist. make sure the output i receive from you is properly formatted with highlighted captions, line breaks between each piece of data and properly formatted to be easier to digest. suggest content gaps or opportunities presented by this video or what it fails to cover\n"
                    + transcript
                )
                    transcript_result = call_openrouter(transcript_prompt, model_map[model_choice])
                    prompt_cost = rates[model_choice][0] * len(transcript_prompt.split()) / 1000
                    total_session_cost += prompt_cost
                    prompt_cost = rates[model_choice][0] * len(transcript_prompt.split()) / 1000  # estimate input cost
                    total_session_cost += prompt_cost
                    st.markdown(markdown.markdown(transcript_result), unsafe_allow_html=True)
            else:
                st.error("No transcript available.")

                st.markdown(f"**💰 Estimated cost for this analysis:** ${total_session_cost:.4f}")
        total_cost = update_total_cost(total_session_cost)


        st.markdown(f"**💰 Estimated cost for this analysis:** ${total_session_cost:.4f}")
        total_cost = update_total_cost(total_session_cost)


        st.subheader("📥 Downloads")
        if comments_csv:
            st.download_button("Download Comments CSV", comments_csv, file_name=f"{title}_comments.csv")
        if comment_result:
            st.download_button("Download Comment Analysis", comment_result, file_name=f"{title}_comment_analysis.txt")
        if transcript_result:
            st.download_button("Download Transcript Analysis", transcript_result, file_name=f"{title}_transcript_analysis.txt")
