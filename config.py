# config.py
import configparser

class Config:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.load_config()

    def load_config(self):
        # API Keys
        self.openai_api_key = self.config['API_KEYS']['openai_api_key']
        self.elevenlabs_api_key = self.config['API_KEYS']['elevenlabs_api_key']

        # Voice Settings
        self.voice_id = self.config['VOICE_SETTINGS']['voice_id'].strip()
        self.stability = float(self.config['VOICE_SETTINGS']['stability'])
        self.similarity_boost = float(self.config['VOICE_SETTINGS']['similarity_boost'])

        # GPT Model
        self.gpt_model = self.config['GPT_SETTINGS']['model']

        # Paths
        self.arduino_output_dir = self.config['PATHS']['arduino_output_dir']
        self.model_output_dir = self.config['PATHS']['model_output_dir']
        self.stl_output_file = self.config['PATHS']['stl_output_file']

        # Commands and Settings
        self.wakeup_word = self.config['SETTINGS']['wakeup_word']
        self.command_time = self.config['COMMANDS']['time']
        self.command_weather = self.config['COMMANDS']['weather']
