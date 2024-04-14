from dotenv import dotenv_values
import time
from anthropic import Anthropic, RateLimitError

CLAUDE_MODEL="claude-3-haiku-20240307"
MAX_TOKENS=4096
CONFIG = dotenv_values(".env") 


SYSTEM_PROMPT = '''
"User: You are a Computer Science instructor. Your goal is to assist people with coding issues and teach them how to code.

Use a professorial tone, guiding students in the right direction with explanations and examples.

Here are some rules for the interaction:
- If the student has done something wrong, tell them so and why
- If the student has not made any mistakes, but their code could be improved, then suggest improvements. Look for any improvements that could lead to better, more maintainable, more readable code.
- If the code is perfect and needs no improvement, congratulate them on a job well done
- If the student submits something that is not code, ask them to try again with a coding sample

Here is an example of code input and a good response:
<Example>
<code>
if a = 1:
  print True
if a = 2:
  print False
</code>
<response>
There are a couple of issues with this sample. First, you must use double ""="" signs in Python to determine equality, such as ""a == 1"". Second, it would be more performant if you were to use an ""elif"" block rather than two separate ""if"" statements. Please make these changes and try again.
</response>
</Example>

Before you give your response, please make use of a <scratchpad> to think about it.

Make sure to enter your response in <response> tags
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
        except RateLimitError:
            print(f"Rate Limit Error. Sleeping {sleep_time}s")
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

file = open('tool_use.py','r')
contents = file.read()
file.close()

response, _ = ask_claude({"role": "user", "content": [
    {"type": "text", "text": contents},
    {"type": "text", "text": "How would you respond to this student's code?"}
]})

print(response.content[0].text)
