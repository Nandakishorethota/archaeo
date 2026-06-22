from app.config import OPENROUTER_API_KEY
from openai import OpenAI

print("KEY:", OPENROUTER_API_KEY[:20])
print("LEN:", len(OPENROUTER_API_KEY))

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "user", "content": "who are you"}
    ]
)

print(response.choices[0].message.content)