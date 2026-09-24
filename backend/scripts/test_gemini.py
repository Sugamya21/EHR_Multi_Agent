import os
import sys

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from google import genai
from app.config.settings import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)


response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Say hello to my EHR project in one sentence."
)


print("\nGemini Response:")
print(response.text)