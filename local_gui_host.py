import streamlit as st
import cv2
import pytesseract
import numpy as np
from PIL import Image, ImageOps
import re
import speech_recognition as sr
import pyttsx3
import sympy as sp
import tempfile
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
        speak("Voice Assistant Activated. Say a math expression.")
        st.info("Listening for a math expression...")
        recognizer.adjust_for_ambient_noise(source)

        try:
            audio = recognizer.listen(source, timeout=10)
            command = recognizer.recognize_google(audio).lower()
            expression = clean_expression(command)

            if expression:
                calculation_result = calculate_expression(expression)
                st.session_state['result'] = calculation_result
                speak(calculation_result)
            else:
                speak("No valid math expression detected.")

        except sr.UnknownValueError:
            speak("Could not understand the command.")
        except sr.RequestError:
            speak("Error with the speech recognition service.")
        except Exception as e:
            speak(f"An error occurred: {str(e)}")

# Streamlit app setup
st.set_page_config(page_title="Math Expression Extractor", page_icon="➗", layout="centered")
st.title("➗ Math Expression Extractor & Evaluator")

# Sidebar Navigation
st.sidebar.title("Options")

option = st.sidebar.radio("Choose Input Method:", ("Upload or Capture Image", "Draw Canvas", "Voice Command"))

# Upload or Capture Image Option
if option == "Upload or Capture Image":
    st.subheader("Upload an Image or Capture One")

    uploaded_file = st.file_uploader("Choose an Image...", type=['png', 'jpg', 'jpeg', 'bmp'])
    captured_image = st.camera_input("Or take a Picture:")

    if uploaded_file or captured_image:
        if captured_image:
            img = Image.open(captured_image)
        else:
            img = Image.open(uploaded_file)

        st.image(img, caption="Selected Image", width=400)

        binary_img = preprocess_image(img)
        expression = extract_expression(binary_img)
        calculation_result = calculate_expression(expression)

        st.success(calculation_result)
        if st.button("🔊 Speak Result"):
            speak(calculation_result)

# Canvas Drawing Option
elif option == "Draw Canvas":
    from streamlit_drawable_canvas import st_canvas

    st.subheader("Draw a Math Expression")
    canvas_result = st_canvas(
        fill_color="black",
        stroke_width=10,
        stroke_color="black",
        background_color="white",
        width=400,
        height=250,
        drawing_mode="freedraw",
        key="canvas"
    )

    if st.button("Extract Expression from Drawing"):
        if canvas_result.image_data is not None:
            img_data = canvas_result.image_data
            img = Image.fromarray((img_data[:, :, 0]).astype('uint8'))  # Take only one channel
            img = ImageOps.invert(img)
            img = img.resize((800, 600))
            binary_img = np.array(img)
            _, binary_img = cv2.threshold(binary_img, 128, 255, cv2.THRESH_BINARY)

            expression = extract_expression(binary_img)
            calculation_result = calculate_expression(expression)

            st.success(calculation_result)
            if st.button("🔊 Speak Result", key="speak_drawing"):
                speak(calculation_result)
        else:
            st.warning("Please draw something first.")

# Voice Command Option
elif option == "Voice Command":
    st.subheader("Voice Command Input")
    if st.button("🎙️ Start Voice Assistant"):
        thread = threading.Thread(target=voice_command_listener)
        thread.start()

    if 'result' in st.session_state:
        st.success(st.session_state['result'])

# Footer
st.markdown(
    """
    ---
    Made with ❤️ by [YourName].
    """
)
