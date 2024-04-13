from dotenv import dotenv_values
import time
import textwrap
from anthropic import Anthropic, RateLimitError

CLAUDE_MODEL="claude-3-haiku-20240307"
MAX_TOKENS=4096
CONFIG = dotenv_values(".env") 

SYSTEM_PROMPT = '''
You are a diligent and fastidious research assistant, helping people to understand the world around them.
Phrase all answers with a calm and helpful demeanor, with emphasis on truthfulness. If you think there may be an error in the data, make sure to call that out.
Before you answer, think through the facts available in <scratchpad> tags. Include all thoughts not intended for the user in <scratchpad> tags. Make sure to include this with every response, even if you are only using a Tool.
Return your final answer to the user in a <response> tag.
'''

client = Anthropic(
    api_key=CONFIG["claude_key"],
)

def handle_tool_use(tool_name, input):
    print(f"---> TOOL USE {tool_name}, INPUT {input}")

    match tool_name:
        case "get_weather":
            return get_weather(input['location'])
        case "get_facts":
            return get_facts(input['topic'])
        case _:
            return "n/a"
        
def get_weather(input):
    if input == "Northsborough, NH":
        return("Did you mean Northborough, MA?")
    return(f"It's 70 and sunny in {input}!")

def get_facts(input):
    return f"Here are some facts about {input}:\n- It is the most sought-after attraction in all of Northsborough, New Hampshire\n- 90% of participants love it!\n- It's purple"

def ask_claude_with_retries(new_message,  messages: list =[]):
    sleep_time = 10
    while True:
        try:
            return ask_claude(new_message, messages)
        except RateLimitError:
            print(f"Rate Limit Error. Sleeping {sleep_time}s")
            time.sleep(sleep_time)
            continue

def ask_claude(new_message, messages: list =[]):
    new_messages = messages + [new_message]
    response = client.beta.tools.messages.create(
        model = CLAUDE_MODEL,
        max_tokens = 4096,
        system=SYSTEM_PROMPT,
        tools = [
            {
                "name": "get_weather",
                "description": "Get the current weather in a given location",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        }
                    },
                    "required": ["location"],
                },
            },
                        {
                "name": "get_facts",
                "description": "Use this tool to get facts about any topic. Assume that this tool is returning definitive answers from a reliable source. You can only look up one topic at a time. For example, if someone asks 'How many people live in Providence, RI?' You would input 'Providence, RI' as the topic.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic for retrieving facts",
                        }
                    },
                    "required": ["location"],
                },
            },
        ],
        messages = new_messages
    )
    return response, new_messages

def main():
    user_content = "I want to go see the Percy Balloon. I generally like things that are orange, but I'm not sure what color it is. I could be persuaded to see something in another color if it's popular enough. The weather also might be awful. Should I go?"
    messages = []
    user_response = None
    while True:
        new_message = {
            "role": "user",
            "content": user_content
        }
        response, messages = ask_claude_with_retries(new_message, messages)
        messages.append({
            "role": "assistant",
            "content": response.content
        })
        if response.stop_reason == "tool_use":
            if len(response.content) > 1:
                thoughts = next(block for block in response.content if block.type == "text").text
                print("---> Thinking\n", textwrap.indent(thoughts, '      '))
            tool_use = next(block for block in response.content if block.type == "tool_use")
            tool_response = handle_tool_use(tool_use.name, tool_use.input)
            user_content = [{
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": tool_response
            }]
        else:
            user_response = response
            break
            
    print("response", str(response.content))



main()