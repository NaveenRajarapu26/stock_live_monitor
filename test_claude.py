import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

ANALYSIS_PROMPT = """
You are analyzing a screenshot from a stock market analyst's live video.

Your task:
Extract only clearly visible information from the chart/screen.

Return JSON only. No markdown. No explanation.

JSON format:
{
  "symbol_or_index": "",
  "timeframe": "",
  "current_visible_price": "",
  "key_levels": [],
  "analyst_condition": "",
  "bullish_or_bearish_bias": "",
  "confidence_score": 0.0,
  "notification_message": ""
}

Rules:
1. Do not guess unclear text or prices.
2. If the screenshot is blurry, keep confidence_score below 0.5.
3. If there is a breakout/breakdown level visible, mention it.
4. This is only for monitoring alerts, not financial advice.
5. notification_message must include: "Please verify before taking any trade."
"""


def encode_image_to_base64(image_path: Path) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def clean_json_response(text: str) -> dict:
    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "", 1).strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "", 1).strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return json.loads(cleaned)


screenshots = sorted(Path("screenshots").glob("*.png"))

if not screenshots:
    raise FileNotFoundError("No screenshots found in screenshots folder.")

latest_screenshot = screenshots[-1]
print(f"Using screenshot: {latest_screenshot}")

image_base64 = encode_image_to_base64(latest_screenshot)

response = client.messages.create(
    model=CLAUDE_MODEL,
    max_tokens=800,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_base64,
                    },
                },
                {
                    "type": "text",
                    "text": ANALYSIS_PROMPT,
                },
            ],
        }
    ],
)

response_text = response.content[0].text
analysis = clean_json_response(response_text)

print(json.dumps(analysis, indent=2))