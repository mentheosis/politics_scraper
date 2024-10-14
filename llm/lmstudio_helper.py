from openai import OpenAI

class LMStudioHelper:
    def __init__(self, base_url="http://localhost:1234/v1", api_key="not-needed"):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
    def generate_content(self, prompt, text):
        completion = self.client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.7
        )
        return completion.choices[0].message.content
         
if __name__ == "__main__":
    helper = LMStudioHelper()
    print(helper.generate_content("Introduce yourself."))