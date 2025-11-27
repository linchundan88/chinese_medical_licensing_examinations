import numpy as np
import pandas as pd
from libs.my_helper_llm import get_llm_client
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
from pathlib import Path
from libs.my_helper_exam import process_llm_prediction, list_instructions, input_text_prefix
import math
parser = argparse.ArgumentParser()
# 'gpt-5.1', 'gpt-5.1-chat-latest', 'gpt-5.1', 'gpt-5-chat-latest', 'gemini-3-pro-preview' Public preview Release date: November 18, 2025
# Qwen-plus and Deepseek-v3.1 support mixed thinking mode, and disable thinking mode by default.
parser.add_argument('--model_name', default='gemini-3-pro-preview')  # deepseek-v3.1 qwen-plus qwen3:32b  gpt-5.1-chat-latest gemini-3-pro-preview
parser.add_argument('--instruction_no', type=int, default=0)
parser.add_argument('--thinking_suffix', default='')  # /think  /no_think
parser.add_argument('--max_workers', type=int, default=1)  # the number of threads.
args = parser.parse_args()

if __name__ == '__main__':
    llm_client = get_llm_client(args.model_name)

    df = pd.read_excel(Path(__file__).resolve().parent / 'results' / 'Chinese_Medical_Licensing_Examination_gemini-3-pro-preview_instruction_no0_.xlsx')
    for (index, record) in df.iterrows():
        if isinstance(record['Prediction Answer'], float) and math.isnan(record['Prediction Answer']) or len(str(record['Prediction Answer'])) == 0:
            input_prompt = record['Question Stem'].replace(' ', '') + ':' + '\n' + f"{record['Question Options']}" + '\n'

            print(input_prompt)
            answer = process_llm_prediction(llm_client, args.model_name, list_instructions[args.instruction_no],
                                        input_text_prefix, input_prompt, thinking_suffix=args.thinking_suffix)
            print(f'answer:{answer}')
            print('\n')

    print('OK')