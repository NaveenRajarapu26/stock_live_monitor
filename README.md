# Stock Live Monitor

A Python-based monitoring tool that captures screenshots from a YouTube Live stock-market stream, analyzes the visual chart content using Claude Vision, and sends alert notifications through Gmail.

This project is built as an MVP for monitoring analyst/chart-based live streams. It is designed to extract visible chart information such as ticker symbols, timeframes, key levels, breakout/breakdown conditions, and short alert messages.

> This tool is for monitoring and alerting only. It does not provide financial advice. Always verify before taking any trade.

---

## Features

* Captures screenshots from a YouTube Live video
* Uses Playwright to open and interact with the browser
* Sends chart screenshots to Claude Vision for analysis
* Extracts structured JSON from the image analysis
* Sends Gmail alert emails with the screenshot attached
* Supports multiple alert recipients
* Saves analysis logs locally
* Can run continuously on a schedule
* Includes separate test files for Gmail, screenshot capture, Claude analysis, and full one-time testing

---

## Project Flow

```text
YouTube Live Video
        ↓
Playwright Screenshot Capture
        ↓
Claude Vision Analysis
        ↓
Structured JSON Output
        ↓
Confidence Check
        ↓
Gmail Alert Notification
```

---

## Tech Stack

* Python
* Playwright
* Anthropic Claude API
* Gmail SMTP
* APScheduler
* python-dotenv
* Pillow

---

## Folder Structure

```text
stock_live_monitor/
│
├── app.py
├── test_gmail.py
├── test_screenshot.py
├── test_claude.py
├── test_full_once.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── screenshots/
└── logs/
```

Note: `screenshots/`, `logs/`, `.env`, and `venv/` should not be pushed to GitHub.

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/NaveenRajarapu26/stock_live_monitor
cd stock_live_monitor
```

---

### 2. Create a virtual environment

For Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

For Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
playwright install
```

---

## Environment Variables

Create a `.env` file in the root folder.

Use `.env.example` as a reference:

```env
YOUTUBE_URL=https://www.youtube.com/watch?v=YOUR_LIVE_VIDEO_ID

ANTHROPIC_API_KEY=your_anthropic_api_key_here
CLAUDE_MODEL=claude-sonnet-4-6

GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_google_app_password_without_spaces
ALERT_TO_EMAIL=email1@gmail.com,email2@yahoo.com,email3@hotmail.com

INTERVAL_MINUTES=5
CONFIDENCE_THRESHOLD=0.70
```

---

## Environment Variable Details

### `YOUTUBE_URL`

The YouTube Live video link that should be monitored.

Example:

```env
YOUTUBE_URL=https://www.youtube.com/watch?v=abc123xyz
```

---

### `ANTHROPIC_API_KEY`

Your Anthropic Claude API key.

Do not share this key or commit it to GitHub.

---

### `CLAUDE_MODEL`

Recommended model:

```env
CLAUDE_MODEL=claude-sonnet-4-6
```

Sonnet is recommended because it gives a good balance between vision quality, cost, and speed.

---

### `GMAIL_USER`

The Gmail account used to send alerts.

Example:

```env
GMAIL_USER=yourname@gmail.com
```

---

### `GMAIL_APP_PASSWORD`

Use a Google App Password, not your normal Gmail password.

The app password should be pasted without spaces.

Example:

```env
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

---

### `ALERT_TO_EMAIL`

The email address or list of email addresses that should receive alerts.

Single recipient:

```env
ALERT_TO_EMAIL=yourname@gmail.com
```

Multiple recipients:

```env
ALERT_TO_EMAIL=email1@gmail.com,email2@yahoo.com,email3@hotmail.com
```

---

### `INTERVAL_MINUTES`

How often the monitor should run.

For testing:

```env
INTERVAL_MINUTES=1
```

For normal use:

```env
INTERVAL_MINUTES=5
```

---

### `CONFIDENCE_THRESHOLD`

Minimum Claude confidence score required before sending an alert.

For testing:

```env
CONFIDENCE_THRESHOLD=0.30
```

For normal use:

```env
CONFIDENCE_THRESHOLD=0.70
```

---

## Running Tests

### Test Gmail

Run this first to confirm Gmail alert sending works:

```bash
python test_gmail.py
```

Expected result:

```text
Test email sent successfully.
```

---

### Test Screenshot Capture

Run:

```bash
python test_screenshot.py
```

This will open the YouTube Live video, play the stream, and save a screenshot inside the `screenshots/` folder.

---

### Test Claude Analysis

Run:

```bash
python test_claude.py
```

This sends the latest screenshot to Claude and prints structured JSON output.

Example output:

```json
{
  "symbol_or_index": "PRFX",
  "timeframe": "30s - NASDAQ",
  "current_visible_price": "8.30-8.50 range",
  "key_levels": ["8.50 resistance"],
  "analyst_condition": "Post-spike breakdown pattern visible",
  "bullish_or_bearish_bias": "BEARISH",
  "confidence_score": 0.55,
  "notification_message": "ALERT: PRFX showing possible breakdown. Please verify before taking any trade."
}
```

---

### Test Full Pipeline Once

Run:

```bash
python test_full_once.py
```

This performs one full cycle:

```text
Capture screenshot → Analyze with Claude → Send Gmail alert → Stop
```

This is useful for testing without running the continuous scheduler.

---

## Run Continuous Monitoring

To start the full scheduled monitor:

```bash
python app.py
```

The app will:

1. Run immediately
2. Capture a screenshot
3. Send it to Claude
4. Send an alert email if confidence is above the threshold
5. Repeat every `INTERVAL_MINUTES`

To stop the app:

```bash
CTRL + C
```

---

## Gmail Setup

This project uses Gmail SMTP.

You need:

1. A Gmail account
2. 2-Step Verification enabled
3. A Google App Password

Do not use your normal Gmail password in the `.env` file.

---

## GitHub Safety

Never commit secrets.

Make sure `.gitignore` includes:

```gitignore
.env
venv/
__pycache__/
*.pyc
logs/
screenshots/
.DS_Store
.vscode/
```

Only commit `.env.example`, not `.env`.

---

## Current MVP Limitations

* The system depends on YouTube video quality
* Blurry charts may reduce Claude confidence
* The model may misread small chart numbers
* It currently uses visual analysis only
* It does not yet validate price levels with real market data
* It may send duplicate alerts if the same condition appears repeatedly
* YouTube page layout changes may affect screenshot capture

---

## Recommended Future Improvements

* Add duplicate alert prevention
* Add real-time market price API confirmation
* Add database storage for alerts
* Add dashboard for monitoring alerts
* Add better screenshot cropping
* Add Docker support
* Add retry mechanism for browser/API failures
* Add WhatsApp or Slack notification support
* Add custom MCP server later if tool-based Claude control is needed

---

## Important Disclaimer

This project is for educational, monitoring, and internship demonstration purposes only.

The alerts generated by this system are based on visual analysis of a live video stream and may be inaccurate. This tool should not be used as financial advice or as an automated trading decision system.

Always verify information from official market data sources before making any trading decision.
