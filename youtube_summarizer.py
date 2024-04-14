import yt_dlp

import requests
import sys
from dotenv import dotenv_values
import time
from anthropic import Anthropic, RateLimitError

CLAUDE_MODEL="claude-3-haiku-20240307"
MAX_TOKENS=4096
CONFIG = dotenv_values(".env") 


SYSTEM_PROMPT = '''
User: You are a research assistant who summarizes videos for professors looking to create educational content. Your goal is to provide an exhaustive summary of the video content, highlighting key points and concepts.

You should aim to provide a summary that is clear, accurate, and informative. Make sure to include any important details and proper nouns (company names, product names, etc) that may be relevant to the video's content.

You will be provided with a subtitles file, which you can use to generate the summary. You can use this information to help you understand the video content and create a summary that is both informative and engaging.

Use markdown styling, bolding proper nouns. Use multiple levels of headers and nested bullet-point format to break the video summary into a logical structure. If the video contains any lists, make sure to represent them as bullet points.
'''


client = Anthropic(
    api_key=CONFIG["claude_key"],
)

def ask_claude_with_retries(new_message, messages: list =[]):
    """
    Sends a message to Claude and retries in case of RateLimitError.

    Args:
        new_message (str): The new message to send to Claude.
        messages (list, optional): List of previous messages. Defaults to an empty list.

    Returns:
        The response from ask_claude.

    """
    sleep_time = 10
    while True:
        try: 
            return ask_claude(new_message, messages)
        except RateLimitError as e:
            print(e, file=sys.stderr)
            print(f"Rate Limit Error. Sleeping {sleep_time}s", file=sys.stderr)

            time.sleep(sleep_time)
            continue

def ask_claude(new_message, messages: list =[]):
    """
    Sends a new message to Claude and returns the response.

    Args:
        new_message (str): The new message to send to Claude.
        messages (list, optional): List of previous messages. Defaults to an empty list.

    Returns:
        tuple: A tuple containing the response from Claude and the updated list of messages.
    """
    new_messages = messages + [new_message]
    response = client.beta.tools.messages.create(
        model = CLAUDE_MODEL,
        max_tokens = 4096,
        system=SYSTEM_PROMPT,
        messages = new_messages
    )
    return response, new_messages

def download_captions(video_url):
    ydl = yt_dlp.YoutubeDL({
        'writesubtitles': True,
        'subtitleslangs': ['en'],
        'writeautomaticsub': True,
        'logtostderr': True,
    })
    res = ydl.extract_info(video_url, download=False)
    if res['requested_subtitles'] and res['requested_subtitles']['en']:
        response = requests.get(res['requested_subtitles']['en']['url'], stream=True)
        return response.text
    else:
        print('This Youtube Video does not have any english captions')
        return None
    
def main(video_url):
    captions = download_captions(video_url)
    if not captions:
        return
    new_message = {
        "role": "user",
        "content": [
            {"type": "text", "text": captions},
            {"type": "text", "text": "Can you summarize the video?"}
        ]
    }
    response, _ = ask_claude_with_retries(new_message)

    print(response.content[0].text)
    

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Error: Please provide a valid YouTube URL as a command line argument.")
        sys.exit(1)
    
    video_url = sys.argv[1]
    if not video_url.startswith("https://www.youtube.com/watch?v="):
        print("Error: Invalid YouTube URL format.")
        sys.exit(1)
    
    main(video_url)