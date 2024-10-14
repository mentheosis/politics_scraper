class LLMChunker:
    def __init__(self, model, chunk_size=4096, overlap=512):
        self.model = model
        self.chunk_size = chunk_size
        self.overlap = overlap
    def generate_content(self, prompt, text):
        chunks = [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size - self.overlap)]
        results = []
        i = 0
        for chunk in chunks:
            print("Processing chunk " + str(i) + " out of " + str(len(chunks)))
            result = self.model.generate_content(None, prompt + "\n" + chunk)
            results.append(result)
            i = i + 1
        return results