from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

def get_llm_client(model_name):

    if model_name in ['deepseek-v3', 'deepseek-v3.1', 'deepseek-r1', 'qwen-plus', 'qwen3-max']:
        client = OpenAI(
            base_url=os.getenv("SERVICE_URL_ali"),
            api_key=os.getenv("API_KEY_ALI"),
        )
    elif model_name in ['gpt-5.1', 'gpt-5.1-chat-latest', 'gpt-5.1', 'gpt-5-chat-latest', 'gemini-3-pro-preview']:
        client = OpenAI(
            base_url=os.getenv("SERVICE_URL_ZZZ"),
            api_key=os.getenv("API_KEY_ZZZ"),
        )
    else:  # locally deployed models using ollama
        client = OpenAI(
            base_url=os.getenv("SERVICE_URL_LOCAL"),
            api_key='ollama',  # required, but unused
        )

    return client