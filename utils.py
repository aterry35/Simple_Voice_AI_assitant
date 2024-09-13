# utils.py
from openai import OpenAI
from config import Config
import logging
from datetime import datetime
import os

config = Config()
client = OpenAI(api_key=config.openai_api_key)

def process_prompt(prompt, config):
    response = client.chat.completions.create(model=config.gpt_model,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ])
    return response.choices[0].message.content

def rename_old_file(file_path):
    if os.path.exists(file_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{file_path}_{timestamp}"
        os.rename(file_path, new_name)
        logging.info(f"Renamed old file to: {new_name}")
