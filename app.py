import os
import json
import base64
import smtplib
from email.message import EmailMessage
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from anthropic import Anthropic
from apscheduler.schedulers.blocking import BlockingScheduler
from playwright.sync_api import sync_playwright


load_dotenv()

YOUTUBE_URL = os.getenv("YOUTUBE_URL")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

INTERVAL_MINUTES = int(os.getenv("INTERVAL_MINUTES", "5"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.70"))

SCREENSHOT_DIR = Path("screenshots")
LOG_DIR = Path("logs")

SCREENSHOT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

client = Anthropic(api_key=ANTHROPIC_API_KEY)


ANALYSIS_PROMPT = """
You are analyzing a screenshot from a stock market analyst's live video.

Your task:
Extract only clearly visible stock/chart information from the screenshot.

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
1. Do not guess unclear text, ticker symbols, or prices.
2. Only include key levels that appear to be actual stock price levels.
3. Ignore random scanner values, volume numbers, timestamps, viewer counts, and unrelated labels.
4. If the chart or text is blurry, keep confidence_score below 0.5.
5. If no clear breakout/breakdown condition is visible, say "No clear condition visible."
6. Do not give financial advice.
7. notification_message must include: "Please verify before taking any trade."
8. Keep the notification short and practical.
"""

def capture_screenshot() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = SCREENSHOT_DIR / f"youtube_live_{timestamp}.png"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1280, "height": 720})

        page.goto(YOUTUBE_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(8000)

        # Try to start the YouTube video
        try:
            page.locator("video").first.click(timeout=10000)
            print("Clicked video player.")
        except Exception:
            try:
                page.keyboard.press("k")
                print("Pressed K to play video.")
            except Exception:
                print("Could not start video, continuing anyway.")

        page.wait_for_timeout(10000)

        # Prefer screenshot of only the video area
        try:
            video = page.locator("video").first
            video.screenshot(path=str(screenshot_path))
            print("Captured video-only screenshot.")
        except Exception:
            page.screenshot(path=str(screenshot_path), full_page=False)
            print("Captured full-page screenshot.")

        browser.close()

    return screenshot_path



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


def analyze_with_claude(image_path: Path) -> dict:
    image_base64 = encode_image_to_base64(image_path)

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
    return clean_json_response(response_text)


def send_email_alert(subject: str, message: str, screenshot_path: Path | None = None) -> None:
    gmail_user = os.getenv("GMAIL_USER")
    gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")
    alert_to_email = os.getenv("ALERT_TO_EMAIL")

    if not gmail_user or not gmail_app_password or not alert_to_email:
        print("Gmail credentials missing. Skipping email notification.")
        return

    recipients = [email.strip() for email in alert_to_email.split(",") if email.strip()]

    email = EmailMessage()
    email["From"] = gmail_user
    email["To"] = ", ".join(recipients)
    email["Subject"] = subject

    email.set_content(message)

    # Optional: attach screenshot with alert
    if screenshot_path and screenshot_path.exists():
        with open(screenshot_path, "rb") as file:
            image_data = file.read()

        email.add_attachment(
            image_data,
            maintype="image",
            subtype="png",
            filename=screenshot_path.name,
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(gmail_user, gmail_app_password)
        smtp.send_message(email, to_addrs=recipients)

    print(f"Email alert sent to {len(recipients)} recipient(s).")



def save_log(data: dict) -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_DIR / f"analysis_{timestamp}.json"

    with open(log_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def run_monitoring_job() -> None:
    print("Running monitoring job...")

    try:
        screenshot_path = capture_screenshot()
        print(f"Screenshot saved: {screenshot_path}")

        analysis = analyze_with_claude(screenshot_path)
        save_log(analysis)

        confidence = float(analysis.get("confidence_score", 0))
        notification_message = analysis.get("notification_message", "")

        if confidence >= CONFIDENCE_THRESHOLD and notification_message:
            send_email_alert(
                subject="Stock Live Monitor Alert",
                message=notification_message,
                screenshot_path=screenshot_path,
            )
            print("Email notification sent.")
        else:
            print(f"No alert sent. Confidence: {confidence}")

    except Exception as error:
        error_message = f"Stock monitor error: {error}"
        print(error_message)

        try:
            send_email_alert(
                subject="Stock Live Monitor Error",
                message=error_message,
            )
        except Exception:
            pass




if __name__ == "__main__":
    print("Starting stock live monitor...")

    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_monitoring_job,
        "interval",
        minutes=INTERVAL_MINUTES,
        next_run_time=datetime.now(),
    )

    scheduler.start()