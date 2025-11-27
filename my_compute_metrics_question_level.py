import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--examination_type', default='Chinese_Medical_Licensing_Examination')
parser.add_argument('--thinking_suffix', default='')  # /think  /no_think
parser.add_argument('--instruction_no', type=int, default=0)
args = parser.parse_args()
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))
sys.path.append(str(Path(__file__).resolve().parent.parent))
import random
import pandas as pd
import numpy as np
from libs.my_helper_ststistics import my_bootstrap
import matplotlib.pyplot as plt
from libs.my_helper_exam import parse_result




if __name__ == '__main__':
    list_mean, list_ci_95_lower, list_ci_95_upper = [], [], []
    random.seed(800)
    np.random.seed(800)
    bar_chart_img_file = (Path(__file__).resolve().parent / 'results' /
                          f'{args.examination_type}_instruction_no{args.instruction_no}_{args.thinking_suffix}_CF.png')

    list_model_name = ['gpt-5.1-chat-latest', 'gemini-3-pro-preview', 'qwen3-max', 'deepseek-v3.1']
    list_model_title = ['ChatGPT-5.1', 'Gemini-3-Pro-Preview', 'Qwen-Max', 'DeepSeek-V3.1']
    for model_name in list_model_name:

        result_excel_file = (Path(__file__).resolve().parent / 'results' /
                             f'{args.examination_type}_{model_name.replace(":", "_")}_instruction_no{args.instruction_no}_{args.thinking_suffix}.xlsx')
        df = pd.read_excel(result_excel_file)

        print(result_excel_file)
        list_prediction_answers, list_correct_answers, list_correct_wrong = [], [], []

        # 'Year', 'Unit', 'Question Type', 'Question_no', 'Question Stem', 'Question Options', 'Correct Answer', 'Prediction Answer'
        for _, record in df.iterrows():
            prediction_answer_str = record['Prediction Answer']
            # if prediction_answer_str.startswith('System Error:'):
            #     continue

            prediction_answer = parse_result(prediction_answer_str)

            list_prediction_answers.append(prediction_answer)
            list_correct_answers.append(record['Correct Answer'])

            if prediction_answer == record['Correct Answer']:
                list_correct_wrong.append(1)
            else:
                list_correct_wrong.append(0)

        correct_rate = np.mean(list_correct_wrong)
        correct_rate = round(correct_rate, 4)
        print(f'Correct Rate: {correct_rate:.4%}')

        lower_correct_rate_95, higher_correct_rate_95 = my_bootstrap(list_correct_wrong, np.mean, c=0.95)
        lower_correct_rate_99, higher_correct_rate_99 = my_bootstrap(list_correct_wrong, np.mean, c=0.99)
        lower_correct_rate_95 = round(lower_correct_rate_95, 4)
        higher_correct_rate_95 = round(higher_correct_rate_95, 4)
        print(f'(lower_correct_rate_95:{lower_correct_rate_95:.4f}~higher_correct_rate_95:{higher_correct_rate_95:.4f})')
        print(f'(lower_correct_rate_99:{lower_correct_rate_99:.4f}~higher_correct_rate_99:{higher_correct_rate_99:.4f})')

        list_mean.append(correct_rate)
        list_ci_95_lower.append(lower_correct_rate_95)
        list_ci_95_upper.append(higher_correct_rate_95)


    # regioon drawing bar chart

    # 计算误差线
    error_95 = [
        [list_mean[i] - list_ci_95_lower[i] for i in range(len(list_mean))],  # 下误差
        [list_ci_95_upper[i] - list_mean[i] for i in range(len(list_mean))]  # 上误差
    ]

    # 绘制柱状图
    plt.figure(figsize=(10, 6))
    bars = plt.bar(
        list_model_title,
        list_mean,
        yerr=error_95,
        capsize=10,
        color=['skyblue', 'lightgreen'],
        alpha=0.7,
        edgecolor='black',
        linewidth=0.5
    )

    plt.axhline(y=0.6, color='red', linestyle='--', linewidth=2, label='Passing Line (0.6)')
    plt.axhline(y=0.53, color='pink', linestyle='--', linewidth=2, label='ChatGPT 3.5 (0.53)')


    # 图形美化
    plt.ylabel('Correct Rate')
    plt.title('Question-Level Accuracy Rates with 95% Confidence Intervals')
    plt.ylim(0, 1)
    plt.legend(bars, ['95% Confidence Interval'], loc='upper right')

    # 显示图形
    plt.savefig(bar_chart_img_file, dpi=600, bbox_inches='tight')
    plt.tight_layout()
    plt.show()
    plt.close()

    # endregion


    print('OK')




