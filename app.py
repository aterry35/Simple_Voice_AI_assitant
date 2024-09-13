# app.py
import openai
import logging
import streamlit as st
import streamlit.components.v1 as components
import speech_recognition as sr
import os
import requests
from playsound import playsound
from datetime import datetime
import pytz

from config import Config
from utils import process_prompt
from microcontroller import process_arduino_code_request
from design import process_3d_model_request

# Initialize the recognizer
recognizer = sr.Recognizer()

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize configuration
config = Config()

# Streamlit UI setup
st.set_page_config(page_title="Friday AI Assistant", layout="centered")
st.markdown("<h1 style='text-align: center; color: red;'>Friday AI Assistant</h1>", unsafe_allow_html=True)

# Embedding the equalizer-style animation using raw HTML and CSS
components.html(
    """
    <style>
    body {
        background-color: black;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        margin: 0;
        overflow: hidden;
    }

    .equalizer {
        display: flex;
        justify-content: space-around;
        width: 200px;
        height: 50px;
    }

    .bar {
        width: 10px;
        height: 100%;
        background-color: red;
        animation: equalize 1s infinite ease-in-out;
    }

    .bar:nth-child(1) { animation-delay: 0.1s; }
    .bar:nth-child(2) { animation-delay: 0.2s; }
    .bar:nth-child(3) { animation-delay: 0.3s; }
    .bar:nth-child(4) { animation-delay: 0.4s; }
    .bar:nth-child(5) { animation-delay: 0.5s; }
    .bar:nth-child(6) { animation-delay: 0.6s; }

    @keyframes equalize {
        0%, 100% {
            transform: scaleY(1);
        }
        50% {
            transform: scaleY(2);
        }
    }
    </style>

    <div class="equalizer">
        <div class="bar"></div>
        <div class="bar"></div>
        <div class="bar"></div>
        <div class="bar"></div>
        <div class="bar"></div>
        <div class="bar"></div>
    </div>
    """,
    height=200,
)

# Function to get the current time in Pacific Standard Time (PST)
def get_current_time():
    timezone = pytz.timezone("America/Los_Angeles")
    current_time = datetime.now(timezone).strftime("%I:%M %p")
    return f"The current time in Pacific Standard Time is {current_time}."

# Function to get the current weather in Tustin, CA
def get_current_weather():
    return "The current weather in Tustin, CA, is 75 degrees Fahrenheit with clear skies."

# Predefined commands
commands_table = {
    config.command_time: get_current_time,
    config.command_weather: get_current_weather,
}

# Function to perform text-to-speech using Eleven Labs
def speak(text):
    st.write(f"Assistant: {text}")  # Display the assistant's response on Streamlit UI
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.voice_id}"
    headers = {
        "xi-api-key": config.elevenlabs_api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": config.stability,
            "similarity_boost": config.similarity_boost
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        audio_data = response.content
        filename = "response.mp3"
        with open(filename, "wb") as f:
            f.write(audio_data)
        playsound(filename)
        os.remove(filename)
    else:
        logging.error(f"Error: Unable to generate speech. Status code: {response.status_code}")
        logging.error(f"Response: {response.text}")

# Function to process commands
def process_command(command):
    st.write(f"User Command: {command}")  # Display the user's command on Streamlit UI
    if command.startswith("provide code for microcontroller"):
        command = command.replace("microcontroller", "arduino")
        process_arduino_code_request(command, config)
        return "Arduino code generation request has been processed."

    elif command.startswith("provide python code to create stl"):
        command += f" and create stl file under directory {config.stl_output_file}"
        process_3d_model_request(command, config)
        return "3D model generation request has been processed."

    elif command in commands_table:
        response = commands_table[command]()
    else:
        response = process_prompt(command, config)
    return response

# Function to listen for the wake-up word
def listen_for_wakeup_word():
    while True:
        with sr.Microphone() as source:
            st.write("Listening for the wake-up word...")  # Display listening status on UI
            audio = recognizer.listen(source)
            try:
                speech_text = recognizer.recognize_google(audio).lower()
                st.write(f"Detected speech: {speech_text}")  # Display detected speech
                if config.wakeup_word in speech_text:
                    return True
            except sr.UnknownValueError:
                st.write("Could not understand the audio.")
                continue
            except sr.RequestError as e:
                logging.error(f"Could not request results; check your network connection. Error: {str(e)}")
                continue

# Function to continuously listen for commands after wake-up
def listen_for_commands():
    while True:
        
        with sr.Microphone() as source:
            st.write("Listening for a command...")  # Display command listening status
            audio = recognizer.listen(source)
            try:
                speech_text = recognizer.recognize_google(audio).lower()
                st.write(f"Recognized command: {speech_text}")  # Display recognized command
                if speech_text:
                    response = process_command(speech_text)
                    st.write(f"Assistant: {response}")  # Display assistant's response
                    speak(response)
            except sr.UnknownValueError:
                st.write("Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                logging.error(f"Could not request results; check your network connection. Error: {str(e)}")

# Main loop
if __name__ == '__main__':
    logging.info(f"Using voice ID: {config.voice_id}")
    st.write("Waiting for the wake-up word...")

    if listen_for_wakeup_word():
        speak("Hello Mr. Terry, what can I do for you?")
        listen_for_commands()
