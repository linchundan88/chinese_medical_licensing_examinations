#!/bin/bash

# bash my_predict.sh > result.txt

instruction_no="0"

#for model_name in  "qwen-plus" "qwen3-max" "deepseek-v3.1" "qwen3:32b" "gpt-oss:120b" "gpt-oss:20b"
for model_name in  "gemini-3-pro-preview"  # "gpt-5.1-chat-latest" "qwen3-max" "deepseek-v3.1"  # "claude-sonnet-4-5-20250929"
do
  echo "model_name: ${model_name}"
  python ./my_predict.py --model_name ${model_name} --examination_type Chinese_Medical_Licensing_Examination --instruction_no ${instruction_no}
done

