import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.uix.textinput import TextInput

import pytesseract
import numpy as np
from PIL import Image, ImageOps
import re
import sympy as sp
import speech_recognition as sr

Window.size = (800, 600)

class MathApp(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.result_label = Label(text="Upload an image or use voice", size_hint=(1, 0.2))
        self.image_widget = KivyImage(size_hint=(1, 0.5))
        self.file_chooser = FileChooserIconView(size_hint=(1, 0.3))
        self.file_chooser.bind(on_selection=self.load_image)

        self.add_widget(self.file_chooser)
        self.add_widget(self.image_widget)

        buttons_layout = BoxLayout(size_hint=(1, 0.1))
        self.voice_btn = Button(text="🎙 Voice Command")
        self.voice_btn.bind(on_press=self.voice_command_handler)
        buttons_layout.add_widget(self.voice_btn)

        self.add_widget(buttons_layout)
        self.add_widget(self.result_label)

    def preprocess_image(self, image):
        image = image.convert('L').resize((800, 600))
        img_array = np.array(image)
        binary = np.where(img_array < 128, 255, 0).astype(np.uint8)
        return Image.fromarray(binary)

    def extract_expression(self, image):
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, config=custom_config)
        return self.clean_expression(text)

    def clean_expression(self, expression):
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

    def calculate_expression(self, expression):
        try:
            result = sp.sympify(expression)
            return f"Extracted: {expression}\nResult: {result.evalf()}"
        except Exception as e:
            return f"Error: {str(e)}"

    def load_image(self, instance, selection):
        if selection:
            try:
                img = Image.open(selection[0])
                binary_img = self.preprocess_image(img)
                expression = self.extract_expression(binary_img)
                result = self.calculate_expression(expression)
                self.result_label.text = result

                # Display in widget
                display_img = binary_img.convert('RGB')
                tex = Texture.create(size=display_img.size)
                tex.blit_buffer(display_img.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
                tex.flip_vertical()
                self.image_widget.texture = tex
            except Exception as e:
                self.result_label.text = f"Failed to process image: {e}"

    def voice_command_handler(self, instance):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            self.result_label.text = "Listening..."
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=10)
                command = recognizer.recognize_google(audio)
                expression = self.clean_expression(command)
                result = self.calculate_expression(expression)
                self.result_label.text = result
            except sr.UnknownValueError:
                self.result_label.text = "Couldn't understand."
            except Exception as e:
                self.result_label.text = f"Error: {e}"

class MathAppMain(App):
    def build(self):
        return MathApp()

if __name__ == '__main__':
    MathAppMain().run()
