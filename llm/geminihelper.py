api_key = "redacted"
import google.generativeai as genai

import time
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import google.generativeai as genai
import time
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

class GeminiWrapper:
    def __init__(self, api_key=api_key):
        genai.configure(api_key=api_key)
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            ]

        self.model = genai.GenerativeModel(model_name="gemini-pro", safety_settings=safety_settings)

    def generate_content(self, prompt, text):
        # Sleep for 6 seconds
        time.sleep(6)
        prompt_parts = prompt + "\n" + text
        response = self.model.generate_content(prompt_parts)
        if (response.prompt_feedback):
            print("Prompt feedback: ", response.prompt_feedback)
        return response.text

    def count_tokens(self, text):
        return self.model.count_tokens(text).total_tokens
