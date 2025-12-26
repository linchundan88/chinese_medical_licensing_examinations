import re


def parse_result(prediction):
    if '</think>' in prediction:
        prediction = re.sub(r"<think>.*?</think>\n?", "", prediction, flags=re.DOTALL)

    for replace_str in ['*', ':', '：', ' ', '\n']:
        prediction = prediction.replace(replace_str, '')

    list_answer = ['A', 'B', 'C', 'D', 'E']
    list_number_answer = ['1', '2', '3', '4', '5']

    if prediction.upper() in list_answer:
        return prediction.upper()

    for answer_num, answer_s in zip(list_number_answer, list_answer):
        if prediction == answer_num:
            return answer_s

    # prediction_str = prediction[0: 20]

    list_patterns = [r'正确答案([ABCDE])', r'正确答案选项是([ABCDE])', r'选项([ABCDE])', r'答案选项([ABCDE])', r'正确答案是选项([ABCDE])',
                    r'正确答案是([ABCDE])', r'正确答案编号([ABCDE])', r'正确答案为选项([ABCDE])', r'答案选项([ABCDE])', r'答案是([ABCDE])',
                    r'答案([ABCDE])',  r'答案为选项([ABCDE])',  r'正确答案的编号是([ABCDE])',  r'正确答案的选项是([ABCDE])', r'最正确的答案是选项([ABCDE])']
    for pattern in list_patterns:
        match = re.search(pattern, prediction)
        if match:
            predicted_answer = match.group(1)
            return predicted_answer

    list_patterns = [r'正确答案([12345])', r'正确答案选项是([12345])', r'选项([12345])', r'答案选项([12345])', r'正确答案是选项([12345])',
                    r'正确答案是([12345])', r'正确答案编号([12345])', r'正确答案为选项([12345])', r'答案选项([12345])',
                    r'答案([12345])',  r'答案为选项([ABCDE])',  r'正确答案的编号是([12345])',  r'正确答案的选项是([12345])', r'最正确的答案是选项([12345])']
    for pattern in list_patterns:
        match = re.search(pattern, prediction)
        if match:
            predicted_answer_num = int(match.group(1))
            return list_answer[predicted_answer_num-1]

    # list_patterns = [r'answer[ABCDE]']
    # for pattern in list_patterns:
    #     match = re.search(pattern, prediction)
    #     if match:
    #         predicted_answer = match.group(0)
    #         return predicted_answer

    list_patterns = [r'[ABCDE]']
    for pattern in list_patterns:
        match = re.search(pattern, prediction)
        if match:
            predicted_answer = match.group(0)
            return predicted_answer

    list_patterns = [r'[12345]']
    for pattern in list_patterns:
        match = re.search(pattern, prediction)
        if match:
            predicted_answer_num = int(match.group(0))
            return list_answer[predicted_answer_num-1]

    list_patterns_unknown = [r'我不知道']
    for pattern in list_patterns_unknown:
        match = re.search(pattern, prediction)
        if match:
            predicted_answer = match.group(0)
            return predicted_answer

    # print(prediction)

    error_msg = f"Error: data parsing error. {prediction}"  # sometimes return no correct answer. 无正确答案
    return error_msg


def process_llm_prediction(chat_client, model_name, str_instruction, input_text_prefix, input_prompt, thinking_suffix=''):

    input_text = input_text_prefix
    input_text += input_prompt
    if thinking_suffix != '':
        input_text += thinking_suffix

    try:
        completion = chat_client.chat.completions.create(
            model=model_name,
            messages=[{'role': 'system', 'content': str_instruction},
                      {'role': 'user', 'content': input_text}],

            # https://www.volcengine.com/docs/82379/1330626?lang=zh
            # extra_body={
            #     "thinking": {
            #         "type": "disabled",
            #         # "type": "enabled",
            #     }
            # }

            # extra_body={"enable_thinking": False}   # useless
            # https://platform.openai.com/docs/api-reference/completions/create#chat-create-stop
            # A Temperature of 0, a Top K of 1, or a Top P of 0 is the same as replacing softmax with the argmax formula.
            # temperature=1,  # it is a scaling factor applied to the log-probs (or logits) prior to the softmax application.
            # A high value for Temperature squeezes all of our options closer to each other, so they have a closer probability, or a small value for Temperature stretches them apart, making the probabilities of each option further apart.
            # top_p=1,  # default value of 1
        )
    except Exception as e:
        error_msg = f"System Error: {e}"
        return error_msg

    if completion.choices is None:
        return 'completion.choices is None'

    prediction = completion.choices[0].message.content
    return prediction


list_instructions = ["您是一个资深的医生，请根据问题描述从给出的五个选项中选择一个最正确的答案，请直接回答该正确答案的编号。",
                     "您是一个资深的医生，下面问题所给出的五个选项中只有一个是最正确的，如果您比较确定那个选项是正确的请直接回答该选项的编号，否则回答我不知道。",
                     "您是一个资深的医生，下面问题所给出的五个选项中只有一个是最正确的。 如果您有90%以上的把握度能够正确回答该问题则请直接回答该选项的编号，否则回答我不知道。如果回答正确得1分，回答我不知道得0分，回答错误得负1分"
                     ]
input_text_prefix = f""  # 请根据题目，从以下五个选项中选择一个最正确的答案，请直接回答正确答案选项。\n
