
import threading
import hashlib
import time
import queue
import os
import pickle

class LLMCache:
    def __init__(self, underlying_llm, cache_size=1000):
        self.cache = {}
        self.lock = threading.Lock()
        self.cache_size = 4096
        self.underlying_llm = underlying_llm
        self.cache_dir = "llm_cache"
        # Make cache_dir if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        # Load cache pkl if it exists
        cache_file = os.path.join(self.cache_dir, "cache.pkl")
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                self.cache = pickle.load(f)
        print("[LLMCache] Cache size: " + str(len(self.cache)))
        
    def generate_content(self, prompt, text):
        # Calculate md5sum of prompt
        if text is None:
            return ""
        if prompt is None:
            prompt = ""
        md5sum = hashlib.md5((prompt+text).encode()).hexdigest()
        # Check if prompt is in cache
        with self.lock:
            if md5sum in self.cache:
                print("[LLMCache] Cache hit for " + md5sum)
                print(text)
                return self.cache[md5sum]
        # Generate content
        result = self.underlying_llm.generate_content(prompt, text)
        # Add result to cache
        with self.lock:
            self.cache[md5sum] = result
            if len(self.cache) > self.cache_size:
                self.cache.pop(next(iter(self.cache)))
        # Serialize entire cache to pkl file
        cache_file = os.path.join(self.cache_dir, "cache.pkl")
        with open(cache_file, 'wb') as f:
            pickle.dump(self.cache, f)
            
            
        return result