from openai import OpenAI
from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL


class AISummaryService:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )

    def generate_summary(
        self,
        repo_name,
        description,
        architecture,
        important_files,
        stats,
    ):
        prompt = f"""
You are a senior software architect.

Analyze this repository and generate:

1. Purpose
2. Tech Stack
3. Architecture Overview
4. Key Components
5. Suggested Starting Files
6. Learning Path (5 steps max)

Repository Name:
{repo_name}

Description:
{description}

Architecture:
{architecture}

Important Files:
{important_files}

Stats:
{stats}

Return concise JSON only:

{{
  "purpose": "...",
  "tech_stack": ["..."],
  "architecture": "...",
  "key_components": ["..."],
  "starting_files": ["..."],
  "learning_path": [
    {{
      "step": 1,
      "file": "...",
      "reason": "..."
    }}
  ]
}}
"""

        response = self.client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert software architect."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1200,
        )

        return response.choices[0].message.content


ai_summary_service = AISummaryService()

print("KEY:", OPENROUTER_API_KEY[:20])