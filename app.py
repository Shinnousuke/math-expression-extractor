import streamlit as st
import pytesseract
import numpy as np
from PIL import Image, ImageOps
import re
import speech_recognition as sr
import pyttsx3
import sympy as sp

# Initialize speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def preprocess_image(image):
    image = image.convert('L')  # Convert to grayscale
    image = image.resize((800, 600))
    img_array = np.array(image)
    binary = np.where(img_array < 128, 255, 0).astype(np.uint8)  # Inverted binary
    return binary

def extract_expression(image):
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, config=custom_config)
    return clean_expression(text)

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
    expression = re.sub(r'[^0-9+\-*/().a-z^]', '', expression)
    return expression

def calculate_expression(expression):
    if not expression:
        return "No valid expression detected."
    try:
        result = sp.sympify(expression)
        return f"Extracted Expression: {expression}\nResult: {result.evalf()}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

def voice_command_handler():
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
                result = calculate_expression(expression)
                st.session_state['result'] = result
                speak(result)
            else:
                st.warning("No valid math expression detected.")
                speak("No valid math expression detected.")

        except sr.UnknownValueError:
            st.error("Could not understand the command.")
            speak("Could not understand the command.")
        except sr.RequestError:
            st.error("Error with the speech recognition service.")
            speak("Error with the speech recognition service.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            speak(f"An error occurred: {str(e)}")

# --- Streamlit UI ---

st.set_page_config(page_title="Math Expression Extractor", page_icon="➗", layout="centered")
st.title("➗ Math Expression Extractor & Evaluator")

st.sidebar.title("Options")
option = st.sidebar.radio("Choose Input Method:", ("Upload or Capture Image", "Draw Canvas", "Voice Command"))

# --- Upload or Capture Image ---
if option == "Upload or Capture Image":
    st.subheader("Upload an Image or Capture One")

    uploaded_file = st.file_uploader("Choose an Image...", type=['png', 'jpg', 'jpeg', 'bmp'])
    captured_image = st.camera_input("Or take a Picture:")

    if uploaded_file or captured_image:
        img = Image.open(captured_image if captured_image else uploaded_file)
        st.image(img, caption="Selected Image", width=400)

        binary_img = preprocess_image(img)
        expression = extract_expression(binary_img)
        result = calculate_expression(expression)

        st.success(result)
        if st.button("🔊 Speak Result"):
            speak(result)

# --- Canvas Drawing ---
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
            img = Image.fromarray((img_data[:, :, 0]).astype('uint8'))  # Use one channel
            img = ImageOps.invert(img).resize((800, 600))
            binary_img = np.where(np.array(img) < 128, 255, 0).astype(np.uint8)

            expression = extract_expression(binary_img)
            result = calculate_expression(expression)

            st.success(result)
            if st.button("🔊 Speak Result", key="speak_canvas"):
                speak(result)
        else:
            st.warning("Please draw something first.")

# --- Voice Command ---
elif option == "Voice Command":
    st.subheader("Voice Command Input")

    if st.button("🎙️ Start Voice Assistant"):
        voice_command_handler()

    if 'result' in st.session_state:
        st.success(st.session_state['result'])

# --- Footer ---
st.markdown(
    """
    ---
    Made with ❤️ by [YourName].
    """
)
