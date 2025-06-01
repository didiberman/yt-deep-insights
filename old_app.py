import os
import re
import pandas as pd
import markdown
import streamlit as st
from datetime import datetime
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# ---------------------- CONFIG ----------------------
YOUTUBE_API_KEY = st.secrets.get("YOUTUBE_API_KEY")
OPENROUTER_API_KEY = st.secrets.get("CLAUDE_API_KEY")
STATIC_PASSWORD = "123"  # Static password set to "123"
COST_FILE = "total_cost.txt"
CACHE_DIR = "cache"
ANALYSIS_DIR = os.path.join(CACHE_DIR, "analysis")

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)

if not YOUTUBE_API_KEY or not OPENROUTER_API_KEY:
    st.error("Missing required API keys in Streamlit secrets.")
    st.stop()

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

# ---------------------- AUTHENTICATION ----------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("Authentication Required")
    password_input = st.text_input("Enter Password:", type="password")
    if st.button("Login"):
        if password_input == STATIC_PASSWORD:
            st.session_state["authenticated"] = True
            st.success("Authentication successful!")
            st.experimental_rerun()  # Use experimental_rerun for Streamlit versions
        else:
            st.error("Incorrect password. Please try again.")
    st.stop()

# ---------------------- SESSION STATE INITIALIZATION ----------------------
if "files_collected" not in st.session_state:
    st.session_state["files_collected"] = []  # Initialize as an empty list

if "video_titles" not in st.session_state:
    st.session_state["video_titles"] = []  # Initialize as an empty list

# ---------------------- STATIC MODEL PRICING ----------------------
# Prices are per 1,000 tokens (input/output)
MODEL_PRICING = {
    "openrouter/quasar-alpha": {"input": 0.0, "output": 0.0},
    "nvidia/llama-3.1-nemotron-ultra-253b-v1:free": {"input": 0.0, "output": 0.0},
    "meta-llama/llama-4-maverick:free": {"input": 0.0, "output": 0.0},
    "deepseek/deepseek-chat-v3-0324": {"input": 0.27, "output": 1.1},
    "anthropic/claude-3-haiku": {"input": 0.25, "output": 1.25},
}

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
        f.write(f"{total:.3f}")
    return total

# ---------------------- COST ESTIMATION FUNCTION ----------------------
def estimate_cost(model_name, input_tokens, output_tokens):
    """
    Estimate the cost of an analysis based on input and output tokens.

    Args:
        model_name (str): The name of the model used.
        input_tokens (int): The number of input tokens.
        output_tokens (int): The number of output tokens.

    Returns:
        float: The estimated cost in dollars.
    """
    if model_name not in MODEL_PRICING:
        st.error(f"⚠️ Pricing information for model {model_name} is not available.")
        return 0.0

    pricing = MODEL_PRICING[model_name]
    input_cost = input_tokens * (pricing["input"] / 1000)  # Cost per input token
    output_cost = output_tokens * (pricing["output"] / 1000)  # Cost per output token

    return round(input_cost + output_cost, 3)  # Return cost rounded to 3 decimal places

# ---------------------- EXTRACT VIDEO ID FUNCTION ----------------------
def extract_video_id(url):
    """
    Extract the video ID from a YouTube URL.

    Args:
        url (str): The YouTube URL.

    Returns:
        str: The extracted video ID, or None if the URL is invalid.
    """
    # Regular expression to match YouTube video URLs
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

# ---------------------- MAIN UI ----------------------
st.title("Your AI Psychological Research Assistant 🍍 Deep YouTube Audience & Content Insights")

urls_input = st.text_area("Enter up to 2 (!) YouTube URLs (one per line):")
mode = st.radio("Choose analysis type:", ["Comments Only", "Transcript Only", "Both"])
model_map = {
    "Quasar (Free)": "openrouter/quasar-alpha",
    "NVIDIA LLaMA (Free)": "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
    "Meta LLaMA (Free)": "meta-llama/llama-4-maverick:free",
    "DeepSeek ($0.27/1k input tokens, $1.10/1k output tokens)": "deepseek/deepseek-chat-v3-0324",
    "Claude ($0.25/1k input tokens, $1.25/1k output tokens)": "anthropic/claude-3-haiku",
}

# Updated AI Model Selection Dropdown (Static Text)
model_choice = st.selectbox(
    "Choose AI Model:",
    options=list(model_map.keys()),  # Static options
    index=0  # Default selection
)
selected_model_name = model_map[model_choice]

# Display static pricing for the selected model
if "Free" in model_choice:
    st.markdown(f"**💰 Pricing for {model_choice}: Free**")
else:
    pricing = MODEL_PRICING[selected_model_name]
    st.markdown(f"""
    **💰 Pricing for {model_choice}:**
    - **Input Tokens:** ${pricing['input']}/1k tokens
    - **Output Tokens:** ${pricing['output']}/1k tokens
    """)

if st.button("Run Analysis"):
    # Clear session state variables before starting a new analysis
    st.session_state["files_collected"].clear()
    st.session_state["video_titles"].clear()
    total_session_cost = 0.0

    urls = [u.strip() for u in urls_input.strip().splitlines() if u.strip()][:2]
    if not urls:
        st.warning("Please enter at least one valid YouTube URL.")
        st.stop()

    for url in urls:
        # Extract video ID from the provided URL
        vid = extract_video_id(url)
        if not vid:
            st.warning(f"Invalid URL: {url}")
            continue

        # Placeholder for fetching video title
        title = f"Video Title for {vid}"  # Replace with actual `get_video_title` function
        st.session_state["video_titles"].append(title)

        # Placeholder for logging video usage
        # Replace with actual `log_video_usage` function
        st.write(f"Logging video usage for {vid}: {title}")
        st.header(f"📺 {title}")

        # Additional analysis logic goes here...
