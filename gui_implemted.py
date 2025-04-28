import streamlit as st
import pytesseract
import cv2
import numpy as np
from PIL import Image, ImageOps
import speech_recognition as sr
import pyttsx3
import sympy as sp
import re
import threading

# Initialize speech engine
engine = pyttsx3.init()

# Function to speak the output
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Preprocess uploaded or captured image
def preprocess_image(image):
    img = np.array(image.convert('L'))  # Convert to grayscale
    img = cv2.resize(img, (800, 600))
    _, binary = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)
    return binary

# Extract mathematical expression using OCR
def extract_expression(image):
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, config=custom_config)
    return clean_expression(text)

# Clean and format the expression
def clean_expression(expression):
    expression = expression.lower()
    replacements = {
        "sine": "sin", "cosine": "cos", "tangent": "tan",
        "logarithm": "log", "square root": "sqrt",
        "times": "", "into": "", "divided by": "/",
        "power": "*", "raise to": "*"
    }
    for word, symbol in replacements.items():
        expression = expression.replace(word, symbol)
    expression = re.sub(r'[^0-9+\-*/().a-z^]', '', expression)  # Keep math-related characters
    return expression

# Evaluate mathematical expression
def calculate_expression(expression):
    if not expression:
        return "No valid expression detected."
    try:
        result = sp.sympify(expression)
        return f"Extracted Expression: {expression}\nResult: {result.evalf()}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

# Voice command handler
def voice_command_listener():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        speak("Voice Assistant Activated. Say a math expression
