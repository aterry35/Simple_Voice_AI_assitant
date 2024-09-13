# microcontroller.py
import os
import re
import logging
from datetime import datetime
from utils import process_prompt, rename_old_file

def extract_arduino_code(response):
    code_block = re.search(r'```cpp(.*?)```', response, re.DOTALL)
    if code_block:
        return code_block.group(1).strip()
    else:
        return None

def process_arduino_code_request(prompt, config):
    response = process_prompt(prompt, config)
    arduino_code = extract_arduino_code(response)

    if arduino_code:
        if not os.path.exists(config.arduino_output_dir):
            os.makedirs(config.arduino_output_dir)

        output_file = os.path.join(config.arduino_output_dir, "output.ino")
        rename_old_file(output_file)

        with open(output_file, "w") as file:
            file.write(arduino_code)

        logging.info(f"Arduino code has been generated and saved to {output_file}")
    else:
        logging.info("No Arduino code was found in the response.")
