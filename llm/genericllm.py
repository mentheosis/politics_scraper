from llm.geminihelper import GeminiWrapper
from llm.llm_cache import LLMCache
from llm.llm_chunker import LLMChunker
from llm.lmstudio_helper import LMStudioHelper

class GenericLLM:
    def __init__(self):
       # self.gemini = GeminiWrapper()
        self.gemini = LMStudioHelper()
        self.gemini_cache = LLMCache(self.gemini)
    def generate_content(self, instructions, text):
        return self.gemini_cache.generate_content(instructions, text)