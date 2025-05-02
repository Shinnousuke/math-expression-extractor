# the one 
# app.py
import streamlit as st
import cv2
import pytesseract
import numpy as np
from PIL import Image, ImageOps
import re
import sympy as sp

def preprocess_image(image):
    img = np.array(image.convert('L'))
    img = cv2.resize(img, (800, 600))
    _, binary = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)
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
        "times": "*", "into": "*", "divided by": "/",
        "power": "**", "raise to": "**"
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

st.set_page_config(page_title="Math Expression Extractor", page_icon="➗", layout="centered")
st.title("➗ Math Expression Extractor & Evaluator")

st.sidebar.title("Options")
option = st.sidebar.radio("Choose Input Method:", ("Upload or Capture Image", "Draw Canvas"))

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
            img = Image.fromarray((img_data[:, :, 0]).astype('uint8'))
            img = ImageOps.invert(img).resize((800, 600))
            binary_img = np.array(img)
            _, binary_img = cv2.threshold(binary_img, 128, 255, cv2.THRESH_BINARY)

            expression = extract_expression(binary_img)
            result = calculate_expression(expression)

            st.success(result)
        else:
            st.warning("Please draw something first.")

st.markdown("---\nMade with ❤️ by [YourName]")
