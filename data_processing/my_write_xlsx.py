import pickle
from openpyxl import Workbook
from pathlib import Path


if __name__ == '__main__':
    file_pkl = Path(__file__).resolve().parent.parent / 'datafiles' / 'question_answer_data.pkl'
    path_excel = Path(__file__).resolve().parent.parent / 'datafiles' / 'Chinese_Medical_Licensing_Examination.xlsx'

    list_years = [2024, 2023, 2022, 2021, 2020]
    list_units = ['第一单元', '第二单元', '第三单元', '第四单元']
    list_question_types = ['A1', 'A2', 'A3/A4', 'B1']

    with open(file_pkl, 'rb') as f:
        data = pickle.load(f)
        list_question_answer = data['questions']
        list_correct_answer = data['answers']


    for year in list_years:
        for unit in range(len(list_units)):
            number_of_questions = 0
            for question_answer in list_question_answer:
                if question_answer['year'] == year and question_answer['unit'] == unit + 1:
                    number_of_questions += 1

            print('year:', year, 'unit:', unit+1, 'Total questions:', number_of_questions)


    for question_answer in list_question_answer:
        if question_answer['year'] == 2023 and question_answer['unit'] == 3:
            print(question_answer['year'], question_answer['unit'], question_answer['question_type'], question_answer['question_no'])

    for current_year in list_years:
        print('current_year', current_year)
        for current_unit in [i+1 for i in range(len(list_units))]:
            total_question = 0
            for current_question_type in list_question_types:
                total_question_type = 0
                for question_answer in list_question_answer:
                    if (question_answer['year'] == current_year and question_answer['unit'] == current_unit and
                            question_answer['question_type'] == current_question_type):
                        total_question_type += 1
                        total_question += 1
                print('unit:', current_unit, 'question_type:', current_question_type,  'Total questions:', total_question_type)
            print('unit:', current_unit, 'Total questions:', total_question)

            total_answer = 0
            for correct_answer in list_correct_answer:
                if correct_answer['year'] == current_year and correct_answer['unit'] == current_unit:
                    total_answer += 1
            print('unit:', current_unit, 'Total answers:', total_answer)

        print('\n')

    wb = Workbook()  # does not support content management
    ws = wb.active
    ws.title = "Exam Questions"
    headers = ['Year', 'Unit', 'Question Type', 'Question_no', 'Question Stem', 'Question Options',  'Correct Answer', 'is_valid']
    ws.append(headers)

    for question, answer in zip(list_question_answer, list_correct_answer):
        if question['year'] != answer['year'] or question['unit'] != answer['unit']:
            raise Exception('Error')

        print(question['year'], question['unit'], question['question_no'], question['question_stem'], question['question_options'], question['question_type'], answer['correct_answer'])

        if question['question_no'] != answer['question_no']:
            raise Exception('Error')

        is_valid = 1
        # contain a table
        if '某地区对500名沙门菌感染患者的感染情况进行调查，情况如下表所示，最能反映该地区沙门菌时长平均情况的是' in question['question_stem']:
            is_valid = 0

        row_data = [
            question['year'],
            question['unit'],
            question['question_type'],
            question['question_no'],
            question['question_stem'],
            str(question['question_options']),  # 转换为字符串，因为可能包含复杂结构
            answer['correct_answer'],
            is_valid
        ]
        ws.append(row_data)

    wb.save(path_excel)
    wb.close()

    print('Excel file created successfully!')

