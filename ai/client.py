import time
import os

from prompt import PROMPT
from openai import OpenAI

class AIClient:
    def __init__(self, api_key: str, url: str, model: str = "gpt-4o"):
        self.client = OpenAI(base_url=url, api_key=api_key)
        self.model = model

    def chat(self, messages: list):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        if response.choices:
            return response.choices[0].message.content

def generate_levels(client: AIClient, prompt: str, model: str = "gpt-4o"):
    messages = [{"role": "user", "content": prompt}]
    level = client.chat(messages)
    return level

def validate_levels(levels: str) -> list[str]:
    return [levels]

def generate_and_validate_levels(client: AIClient, prompt: str, num_request: int, delay: int = 10):
    for _ in range(num_request):
      try:
        levels = generate_levels(client, prompt)
        valid_levels = validate_levels(levels)
        with open("genereted_levels.txt", "a") as f:
          for levels in valid_levels:
              f.write(levels + "\n")
      except Exception as e:
        print(e)
      print("zzz\n")
      time.sleep(delay)

    return valid_levels

def main():
    api_key = os.getenv("TOKEN")
    url = os.getenv("URL")
    client = AIClient(api_key, url)

    num_requests = 1000
    delay = 10

    generate_and_validate_levels(client, PROMPT, num_requests, delay)



if __name__ == "__main__":
    main()