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