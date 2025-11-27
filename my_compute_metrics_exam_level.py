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
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from libs.my_helper_exam import parse_result
from scipy import stats
from libs.my_helper_ststistics import my_bootstrap




if __name__ == '__main__':

    def plot_exam_results(list_result_year_all, model_name, image_file):
        """
        使用list_result_year_all绘制柱状图
        """

        # 设置中文字体支持
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        # 准备数据
        years = list(range(2020, 2025))  # 2020-2024年
        categories = ['Overall', 'Unit 1', 'Unit 2', 'Unit 3', 'Unit 4']

        # 转换数据格式以便绘图
        data = np.array(list_result_year_all)

        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 8))

        # 设置柱状图参数
        x = np.arange(len(years))  # 年份位置
        bar_width = 0.15  # 柱子宽度
        opacity = 0.8  # 透明度

        # 为每个类别绘制柱状图
        for i, category in enumerate(categories):
            bars = ax.bar(
                x + i * bar_width,
                data[:, i],
                bar_width,
                alpha=opacity,
                label=category
            )

            # 在柱子上添加数值标签
            for j, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.,
                    height + 0.01,
                    f'{height:.3f}',
                    ha='center',
                    va='bottom',
                    fontsize=8
                )

        # 添加及格线 (y=0.6)
        ax.axhline(y=0.6, color='red', linestyle='--', linewidth=1, label='Passing Line (0.6)')
        ax.axhline(y=0.53, color='pink', linestyle='--', linewidth=1, label='ChatGPT 3.5 (0.53)')

        # 设置图表属性
        ax.set_xlabel('Year')
        ax.set_ylabel('Correct Rate')
        ax.set_title(f'Accuracy Rates of Model:{model_name} by Year(2020-2024) and Unit\n')
        ax.set_xticks(x + bar_width * 2)
        ax.set_xticklabels(years)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        # 设置y轴范围
        ax.set_ylim(0, 1.0)


        # 调整布局并显示
        plt.tight_layout()
        # plt.tight_layout(rect=[0, 0, 1, 0.93])  # 为标题预留顶部空间
        # plt.subplots_adjust(top=0.93)  # 设置图表顶部边缘位置，为标题留出空间

        plt.savefig(image_file, dpi=600, bbox_inches='tight')
        plt.show()
        plt.close()

    list_years = [year for year in range(2020, 2025)]
    list_units = [1, 2, 3, 4]  # '第一单元', '第二单元', '第三单元', '第四单元'
    random.seed(800)
    np.random.seed(800)

    list_model_name = ['gpt-5.1-chat-latest', 'gemini-3-pro-preview', 'qwen3-max', 'deepseek-v3.1']
    list_model_title = ['ChatGPT-5.1', 'Gemini-3-Pro-Preview', 'Qwen-Max', 'DeepSeek-V3.1']

    for model_name, model_title in zip(list_model_name, list_model_title):
        print(f'Model: {model_name}')

        result_excel_file = (Path(__file__).resolve().parent / 'results' /
                             f'{args.examination_type}_{model_name.replace(":", "_")}_instruction_no{args.instruction_no}_{args.thinking_suffix}.xlsx')
        df = pd.read_excel(result_excel_file)
        # 'Year', 'Unit', 'Question Type', 'Question_no', 'Question Stem', 'Question Options', 'Correct Answer', 'Prediction Answer'
        bar_chart_img_file = (Path(__file__).resolve().parent / 'results' /
                              f'{args.examination_type}_{model_name.replace(":", "_")}_instruction_no{args.instruction_no}_{args.thinking_suffix}.png')

        list_result_year_unit = []
        list_result_year = []

        for year in list_years:
            # region by year
            result_current_year = []

            df_year = df[df['Year'] == year]
            list_prediction_answers, list_correct_answers, list_correct_wrong = [], [], []

            for _, record in df_year.iterrows():
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

            result_current_year.append(correct_rate)
            list_result_year.append(correct_rate)

            print(f'Year: {year}, Correct Rate: {correct_rate:.3%}')

            # endregion

            # by year and unit
            for unit in list_units:
                df_year_unit = df_year[df_year['Unit'] == unit]
                list_prediction_answers, list_correct_answers, list_correct_wrong = [], [], []

                # 'Year', 'Unit', 'Question Type', 'Question_no', 'Question Stem', 'Question Options', 'Correct Answer', 'Prediction Answer'
                for _, record in df_year_unit.iterrows():
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

                result_current_year_unit = round(np.mean(list_correct_wrong), 4)
                result_current_year.append(result_current_year_unit)

                print(f'Year: {year}, Unit: {unit}, Correct Rate: {result_current_year_unit:.4%}')

            list_result_year_unit.append(result_current_year)

        year_mean = round(np.mean(list_result_year), 4)
        year_sd = round(np.std(list_result_year), 4)

        print(f'Year Sample Mean: {year_mean:.3%}, Year SD: {year_sd:.4%}')

        # region compute confidence interval using two different methods

        lower_correct_rate_95, higher_correct_rate_95 = my_bootstrap(list_result_year, np.mean, c=0.95)
        print(f"95% Confidence Interval using bootstrapping: [{lower_correct_rate_95:.4f}, {higher_correct_rate_95:.4f}]")

        sample_size = len(list_result_year)
        standard_error = year_sd / np.sqrt(sample_size)
        # using t distribution to compute 95% CIs (small sample size)
        t_critical = stats.t.ppf(0.975, df=sample_size - 1)  # 双尾检验，95%置信区间对应0.975分位点
        margin_of_error = t_critical * standard_error
        confidence_interval_lower = year_mean - margin_of_error
        confidence_interval_upper = year_mean + margin_of_error
        print(f"95% Confidence Interval using t distribution: [{confidence_interval_lower:.4f}, {confidence_interval_upper:.4f}]")
        # endregion


        plot_exam_results(list_result_year_unit, model_title, bar_chart_img_file)


    print('OK')

