# 3d_design.py
import os
import re
import logging
import subprocess
import time
import pyautogui
from utils import process_prompt, rename_old_file

def extract_code(response):
    code_blocks = re.findall(r'```python(.*?)```', response, re.DOTALL)
    if code_blocks:
        return "\n".join(code_blocks).strip()
    else:
        return None

def process_3d_model_request(prompt, config):
    response = process_prompt(prompt, config)
    python_code = extract_code(response)

    if python_code:
        if not os.path.exists(config.model_output_dir):
            os.makedirs(config.model_output_dir)

        model_file = os.path.join(config.model_output_dir, "model.py")
        rename_old_file(model_file)
        rename_old_file(config.stl_output_file)

        with open(model_file, "w") as file:
            file.write(python_code)

        logging.info(f"3D model code has been generated and saved to {model_file}")

        result = subprocess.run(["python3", model_file], capture_output=True, text=True)
        logging.info(result.stdout)
        logging.info(f"STL file '{config.stl_output_file}' has been generated.")

        os.system('open /Applications/BambuStudio.app')
        time.sleep(5)

        pyautogui.keyDown('command')
        time.sleep(0.1)
        pyautogui.press('i')
        time.sleep(0.1)
        pyautogui.keyUp('command')

        time.sleep(1)

        abs_stl_file_path = os.path.abspath(config.stl_output_file)
        pyautogui.typewrite(abs_stl_file_path, interval=0.05)
        time.sleep(1)

        pyautogui.press('enter')
        time.sleep(1)

        pyautogui.press('enter')

        logging.info(f"STL file '{config.stl_output_file}' imported into Bambu Studio successfully!")
    else:
        logging.info("No 3D model code was found in the response.")
