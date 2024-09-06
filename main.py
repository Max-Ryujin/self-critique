import json
import openai
import os
import argparse



# Initialize the argument parser
parser = argparse.ArgumentParser(description='Reasoning Task Solver')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Increase output verbosity')
parser.add_argument('-m', '--model', type=str, default="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                    help='The model to use for the reasoning task')
parser.add_argument('-a', '--api', type=str, default="groq", help='The API to use for the reasoning task. select groq or together')

parser.add_argument('-l', '--limit', type=int, default=6, help='The maximum number loops for the self critque loop')

# Parse arguments from the command line
args = parser.parse_args()

# load GROQ api key and if not available try together api key
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")


if args.api == "groq" and GROQ_API_KEY is None:
    raise ValueError("Please set GROQ_API_KEY in your environment variables")
elif args.api == "together" and TOGETHER_API_KEY is None:
    raise ValueError("Please set TOGETHER_API_KEY in your environment variables")
elif args.api == "groq" and GROQ_API_KEY is not None:
    client = openai.OpenAI(api_key=GROQ_API_KEY,
    base_url='https://api.groq.com/openai/v1',
    )
    if args.model == "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo":
        args.model = "llama-3.1-70b-versatile"
elif args.api == "together" and TOGETHER_API_KEY is not None:
    client = openai.OpenAI(api_key=TOGETHER_API_KEY,
    base_url='https://api.together.xyz',
    )
else:
    raise ValueError("Please set GROQ_API_KEY or TOGETHER_API_KEY in your environment variables")

print("Using model:", args.model)
print("Using API:", args.api)


def query_llm(prompt, max_tokens=8000):

    input = f"return the answer to this promt in json format. use the key response and the value as the response. Here is the prompt: {prompt}"
    message = [
        {"role": "system", "content": "You are part of a self critque loop. To make this work it is important to answer in correctly formatted json. always use the keys \"response\" and the response as value or the key \"perfect_response\" and the value true."},
        {"role": "user", "content": input}
    ]

    response = client.chat.completions.create(
        messages=message,
        model=args.model,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )

    return response.choices[0].message.content.strip()


def build_input(prompt, last_response):
    # create a prompt for the model with json that includes the first question, the last response
    # and the task to improve the response or return a json that indicates that the response is perfect

    json_input = {
        "prompt": prompt,
        "last_response": last_response,
        "task": "Given the prompt and the last response, improve the response. The response should be factually accurate and logically sound."
        "It should be well written and should fallow the instructions in the prompt perfectly. Do not use \ n as it breakes the json. If the response is already perfect"
        "write a json response that contains the key perfect_response and the value true. Otherwise, write a json response that contains the key response and the response as value."
    }
    return json_input



def self_critique(prompt, max_tokens=8000):
    loop_counter = 0

    response = query_llm(prompt, max_tokens=max_tokens)
    perfect_response = False

    while not perfect_response:

        input = build_input(prompt, response)

        response = query_llm(input, max_tokens=max_tokens)
        if args.verbose:
            print(response)

        if "perfect_response" in response:
            perfect_response = True
            return response
        else:
            response = json.loads(response)["response"]

        loop_counter += 1
        if loop_counter > args.limit:
            return response
        

def main():
    while True:
        prompt = input("Enter the prompt: ")
        response = self_critique(prompt)
        print(response)
        

__name__ == "__main__" and main()