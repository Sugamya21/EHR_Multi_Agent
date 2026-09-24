import json
from google import genai

from app.config.settings import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def analyze_trends(relevant_data):
    compact_data = {
        "patient": relevant_data.get("patient", [])[:1],
        "conditions": relevant_data.get("conditions", []),
        "medications": relevant_data.get("medications", []),
        "observations": relevant_data.get("observations", [])[-50:],
        "encounters": relevant_data.get("encounters", [])[-20:],
        "procedures": relevant_data.get("procedures", [])[-20:],
        "carePlans": relevant_data.get("carePlans", [])
    }

    prompt = f"""
You are an EHR clinical analysis assistant.

Analyze ONLY the provided patient EHR data.

Return a concise factual clinical analysis containing:

1. overview
2. trends
3. recentChanges

The overview should summarize the patient's documented medical
history, conditions, medications, important observations,
encounters, procedures and care plans.

Trends should describe chronological patterns that are explicitly
supported by repeated or changing records.

Recent changes should describe recent documented changes in the
patient's record.

STRICT RULES:

- Use ONLY the supplied EHR data.
- Do not invent information.
- Do not diagnose the patient.
- Do not recommend treatment.
- Do not recommend medications.
- Do not make predictions.
- Do not infer a disease from a measurement alone.
- Do not treat one isolated measurement as a trend.
- Do not invent allergies.
- Do not invent reference ranges.
- Do not invent a reason for visit.
- Do not invent missing clinical information.
- If information is unavailable, state that it is unavailable.
- Keep the overview concise.
- Keep trends concise.
- Keep recent changes concise.
- Return ONLY valid JSON.
- Do not return markdown.
- Do not use code fences.

Return EXACTLY this JSON structure:

{{
    "overview": "",
    "trends": [
        {{
            "category": "",
            "description": "",
            "evidence": []
        }}
    ],
    "recentChanges": [
        {{
            "category": "",
            "description": "",
            "evidence": []
        }}
    ]
}}

PATIENT EHR:

{json.dumps(compact_data, ensure_ascii=False)}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    response_text = response.text.strip()

    if response_text.startswith("```json"):
        response_text = response_text[7:]

    elif response_text.startswith("```"):
        response_text = response_text[3:]

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    try:
        result = json.loads(response_text)

    except json.JSONDecodeError:
        raise ValueError(
            "Gemini returned invalid clinical analysis JSON."
        )

    return {
        "overview": result.get(
            "overview",
            "No clinical overview available."
        ),
        "trends": result.get(
            "trends",
            []
        ),
        "recentChanges": result.get(
            "recentChanges",
            []
        )
    }