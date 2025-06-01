# AI Psychological Research Assistant

## Project Description

This Streamlit-based web application is designed to help content creators and researchers understand real user feedback and content patterns from YouTube videos. By fetching and analyzing video transcripts and comments using various language models via the OpenRouter API, the tool provides insights that enable you to create more effective and targeted content.

## Features

*   Fetch YouTube video transcripts using the `youtube-transcript-api`.
*   Retrieve YouTube video comments using the YouTube Data API v3.
*   Utilize various language models (LLama-Nvidia, Google Gemini, Meta Maverick, Grok, GPT 4.1 Nano, DeepSeek) via the OpenRouter API.
*   Cache retrieved transcripts and comments for faster access and reduced API calls.
*   Password protection for accessing the application.
*   Download analyzed data (functionality inferred from file structure and common patterns in such apps).

## Technical Specifications

### Dependencies

The project relies on the following Python libraries, as specified in `requirements.txt`:

*   `streamlit`
*   `pandas`
*   `markdown`
*   `google-api-python-client`
*   `google-generativeai`
*   `youtube-transcript-api`
*   `streamlit-cookies-manager`
*   `tiktoken`
*   `requests` (inferred from `ui.py`)

### APIs Used

*   **YouTube Data API v3:** Used for fetching video comments and titles. Requires an API key.
*   **OpenRouter API:** Used for interacting with various language models. Requires an API key.

### Caching

Transcripts and comments are cached locally in the `./cache` directory to minimize repeated API calls.

## Setup and Installation

1.  Clone the repository:

    ```bash
    git clone <repository_url>
    cd yt-deep-insights
    ```

2.  Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3.  Obtain API keys for the YouTube Data API v3 and OpenRouter API.

4.  Configure API keys:

    *   Create a `.streamlit/secrets.toml` file in the project root directory.
    *   Add your API keys to this file:

        ```toml
        YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"
        OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY"
        # CLAUDE_API_KEY may also be needed if used directly, otherwise OpenRouter handles it
        ```

5.  (Optional) Configure proxy settings if needed by adding `PROXY_URL = "your_proxy_url"` to `.streamlit/secrets.toml`.

## Usage

1.  Run the Streamlit application:

    ```bash
    streamlit run ui.py
    ```

2.  Access the application in your web browser at the provided local URL (usually `http://localhost:8501`).

3.  Enter the password to unlock the application (password found in `ui.py` - **Note: It is highly recommended to secure this password properly, e.g., using Streamlit secrets.**).

4.  Use the application interface to input YouTube video URLs and perform analysis.
