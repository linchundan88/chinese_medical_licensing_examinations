# sys.path.append(str(Path(__file__).resolve().parent))
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import time
from pathlib import Path
from libs.my_helper_llm import get_llm_client
from libs.my_helper_exam import process_llm_prediction, list_instructions, input_text_prefix
from openpyxl import Workbook
parser = argparse.ArgumentParser()
# 'gpt-5.1', 'gpt-5.1-chat-latest', 'gpt-5.1', 'gpt-5-chat-latest', 'gemini-3-pro-preview' Public preview Release date: November 18, 2025
# Qwen-plus and Deepseek-v3.1 support mixed thinking mode, and disable thinking mode by default.
# deepseek-v3.1 deepseek-v3.2 deepseek-cha qwen-plus qwen3:32b  gpt-5.1-chat-latest gemini-3-pro-preview  claude-sonnet-4-5  doubao-seed-1.6
parser.add_argument('--model_name', default='doubao-seed-1.6')
parser.add_argument('--examination_type', default='Chinese_Medical_Licensing_Examination')
parser.add_argument('--instruction_no', type=int, default=0)
parser.add_argument('--thinking_suffix', default='')  # /think  /no_think
parser.add_argument('--max_workers', type=int, default=1)  # the number of threads.
args = parser.parse_args()



if __name__ == '__main__':

    llm_client = get_llm_client(args.model_name)

    path_save_results = Path(__file__).resolve().parents[0] / 'results'
    path_save_results.mkdir(exist_ok=True, parents=True)
    path_excel_result = path_save_results / f'{args.examination_type}_{args.model_name.replace(":", "_")}_instruction_no{args.instruction_no}_{args.thinking_suffix}.xlsx'

    df = pd.read_excel(Path(__file__).resolve().parent / 'datafiles' / f'{args.examination_type}.xlsx')
    df = df[df['is_valid'] == 1]

    list_answers = []
    start_time = time.time()

    if args.max_workers > 1:
        with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            futures = [executor.submit(process_llm_prediction, llm_client, args.model_name, list_instructions[args.instruction_no],
                                       input_text_prefix,
                                       record['Question Stem'].replace(' ', '') + ':' + '\n' + f"{record['Question Options']}" + '\n',
                                       args.thinking_suffix) for _, record in df.iterrows()]

            for future in as_completed(futures):
                answer = future.result()
                list_answers.append(answer)
    else:  # single thread
        for (index, record) in df.iterrows():
            input_prompt = record['Question Stem'].replace(' ', '') + ':' + '\n' + f"{record['Question Options']}" + '\n'

            answer = process_llm_prediction(llm_client, args.model_name, list_instructions[args.instruction_no],
                                            input_text_prefix, input_prompt, thinking_suffix=args.thinking_suffix)
            # print(f'index:{index}, prediction:{answer}')
            # print(answer)
            # if len(answer) > 50:
            #     print('aaa')
            print(f'index:{index}')
            list_answers.append(answer)

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"execution time: {execution_time:.2f} seconds")

    # region save results to excel file
    wb = Workbook()  # does not support content management
    ws = wb.active
    ws.title = "Exam Questions"
    headers = ['Year', 'Unit', 'Question Type', 'Question_no', 'Question Stem', 'Question Options',  'Correct Answer', 'Prediction Answer']
    ws.append(headers)

    # when using the method iterrow(), the index is not correct because of  using df filter beforehand.
    index = 0
    for _, row in df.iterrows():
        prediction_answer = list_answers[index]

        row_data = [
            row['Year'],
            row['Unit'],
            row['Question Type'],
            row['Question_no'],
            row['Question Stem'],
            str(row['Question Options']),  # 转换为字符串，因为可能包含复杂结构
            row['Correct Answer'],
            prediction_answer
        ]
        ws.append(row_data)

        index += 1

    wb.save(path_excel_result)
    wb.close()

    # endregion

    print('OK.')

'''
qwen3-max
execution time: 3093.16 seconds

Qwen-plus
execution time: 1600.83 seconds

DeepSeek-V3.1
execution time: 2027.51 seconds

Chat GPT 5.1
execution time: 7066.39 seconds

gemini-3-pro-preview
start 751.6476 元   411.9346 元  339 RMB
execution time: 95896.81 seconds
execution time: 46598.24 seconds  2025—12-14


DeepSeek-V3.2 
execution time: 5014.31 seconds ali cloud
deepseek platform  execution time: 3514.51 seconds


gpt-5.2-chat-latest
8 RMB
execution time: 9316.75 seconds

claude-sonnet-4-5   it is a thinking model.
182 RMB
execution time: 32203.30 seconds

doubao-seed-1.6  
3.8 RMB
execution time: 37557.77 seconds


'''