from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

def get_llm_client(model_name):

    if model_name in ['qwen-plus', 'qwen3-max', 'deepseek-v3.1', 'deepseek-v3.2',]:
        client = OpenAI(
            base_url=os.getenv("SERVICE_URL_ali"),
            api_key=os.getenv("API_KEY_ALI"),
        )
    elif model_name in ['gpt-5.1', 'gpt-5.1-chat-latest', 'gpt-5.2-chat-latest', 'gpt-5.1', 'gpt-5-chat-latest', 'gemini-3-pro-preview','doubao-seed-1.6',
                        'claude-sonnet-4-5']:
        client = OpenAI(
            base_url=os.getenv("SERVICE_URL_ZZZ"),
            api_key=os.getenv("API_KEY_ZZZ"),
        )
    elif model_name in ['doubao-seed-1-6-251015']:
        client = OpenAI(
            base_url=os.getenv("SERVICE_URL_HUOSHAN"),
            api_key=os.getenv("API_KEY_HUOSHAN"),
        )
    elif model_name in ['deepseek-v3',  'deepseek-r1', 'deepseek-chat']:
        client = OpenAI(
            base_url=os.getenv("SERVICE_URL_DEEPSEEK"),
            api_key=os.getenv("API_KEY_DEEPSEEK"),
        )
    else:  # locally deployed models using ollama
        client = OpenAI(
            base_url=os.getenv("SERVICE_URL_LOCAL"),
            api_key='ollama',  # required, but unused
        )

    return client