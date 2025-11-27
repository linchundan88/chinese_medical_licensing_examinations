
import pandas as pd
from pathlib import Path
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--examination_type', default='Chinese_Medical_Licensing_Examination')
parser.add_argument('--thinking_suffix', default='')  # /think  /no_think
parser.add_argument('--instruction_no', type=int, default=0)
args = parser.parse_args()


if __name__ == '__main__':
    list_model_name = ['gpt-5.1-chat-latest', 'gemini-3-pro-preview', 'qwen3-max', 'deepseek-v3.1']
    list_model_title = ['ChatGPT-5.1', 'Gemini-3-Pro-Preview', 'Qwen-Max', 'DeepSeek-V3.1']

    for model_name, model_title in zip(list_model_name, list_model_title):
        print(f'Model: {model_name}')

        result_excel_file = (Path(__file__).resolve().parent / 'results' /
                             f'{args.examination_type}_{model_name.replace(":", "_")}_instruction_no{args.instruction_no}_{args.thinking_suffix}.xlsx')

        num_length = 0

        df = pd.read_excel(result_excel_file)
        for _, record in df.iterrows():
            prediction_answer_str = record['Prediction Answer']
            num_length += len(prediction_answer_str)

        print(f'Average Prediction {num_length / len(df):.4f}')



    print('OK')