# claude-experiments

Current experiments:
  - `tool_use.py`
    - Some mocked/static data to explore Claude's new [Function Calling](https://docs.anthropic.com/claude/docs/tool-use) capabilities. Test prompt requires multiple calls to different tools.
  - `code_instructor.py`
    - Sends Claude the code from `tool_use.py`, asking it for feedback
  - `youtube_summarizer`
    - Takes in a Youtube URL as a CLI parameter, downloads the captions content via [yt-dlp](https://github.com/yt-dlp/yt-dlp), and asks Claude to summarize the video in Markdown format
    - example usage: `python youtube_summarizer.py https://www.youtube.com/watch?v=kJvXT25LkwA > test.md`