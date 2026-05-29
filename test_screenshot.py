import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

YOUTUBE_URL = os.getenv("YOUTUBE_URL")
SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)

if not YOUTUBE_URL:
    raise ValueError("YOUTUBE_URL missing in .env file")

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
screenshot_path = SCREENSHOT_DIR / f"test_youtube_playing_{timestamp}.png"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={"width": 1280, "height": 720})

    page.goto(YOUTUBE_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(8000)

    # Try to click the video/play button
    try:
        page.locator("video").first.click(timeout=10000)
        print("Clicked video player.")
    except Exception:
        try:
            page.keyboard.press("k")
            print("Pressed K to play video.")
        except Exception:
            print("Could not click play, continuing anyway.")

    page.wait_for_timeout(10000)

    # Take screenshot of full page
    page.screenshot(path=str(screenshot_path), full_page=False)

    browser.close()

print(f"Screenshot saved successfully: {screenshot_path}")