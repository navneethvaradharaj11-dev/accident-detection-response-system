# Smart Accident Detection and Response System

A Python-based accident detection and emergency response dashboard that demonstrates a complete escalation workflow: accident detection, alarm activation, driver response countdown, SMS notification, contact acknowledgement wait time, and automatic call escalation through Twilio.

The project includes both a browser dashboard and a Tkinter desktop dashboard, so it can be demonstrated on almost any Windows, macOS, or Linux machine with Python installed.

## Features

- Real-time accident event simulation
- 30-second driver response timer
- Emergency SMS workflow
- 15-second contact acknowledgement timer
- Automatic call escalation when acknowledgement is missed
- Editable vehicle, location, and emergency contact details
- Contact-level SMS and call status tracking
- Demo mode for safe presentations without sending real alerts
- Twilio REST integration for real SMS and voice calls
- Web dashboard plus Tkinter desktop interface

## Project Structure

```text
.
├── accident_ui.py              # Tkinter desktop dashboard
├── web_dashboard.py            # Browser dashboard server
├── twilio.py                   # Twilio REST helper and message builders
├── static/
│   ├── app.js                  # Dashboard client behavior
│   └── styles.css              # Dashboard styling
├── templates/
│   ├── index.html              # Main dashboard page
│   ├── garage_setup.html       # Setup view
│   └── service_bay.html        # Service/diagnostics view
├── requirements.txt
└── .github/workflows/
    └── ci.yml                  # GitHub Actions validation
```

## Requirements

- Python 3.10 or newer
- A Twilio account only if you want to send real SMS or place real calls

Install the Python dependency:

```powershell
pip install -r requirements.txt
```

## Quick Start

Run the web dashboard:

```powershell
python web_dashboard.py
```

Open the dashboard in your browser:

```text
http://127.0.0.1:8080
```

To prevent the app from opening a browser automatically:

```powershell
python web_dashboard.py --no-browser
```

To use a different port:

```powershell
python web_dashboard.py --port 8125
```

Run the Tkinter desktop dashboard:

```powershell
python accident_ui.py
```

## Notification Modes

The dashboard starts in demo mode when Twilio credentials are missing. Demo mode is safe for presentations because it simulates SMS and call delivery without contacting Twilio.

To enable real SMS and voice calls:

1. Copy `.env.example` to `.env`.
2. Fill in your Twilio credentials and phone numbers.
3. Start the dashboard.
4. Turn demo mode off from the dashboard settings.

Example `.env` values:

```text
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+14155552671
TWILIO_TO_NUMBER=+919876543210
DASHBOARD_DEMO_MODE=true
```

Keep `.env` private. It is intentionally ignored by git.

## How The Emergency Workflow Works

1. The system enters normal monitoring mode.
2. An accident event is triggered from the dashboard.
3. The alarm activates and a 30-second driver response timer starts.
4. If the driver confirms safety, the workflow resets.
5. If the timer expires, SMS alerts are sent to emergency contacts and responders.
6. A 15-second acknowledgement timer starts.
7. If no contact acknowledges, the system escalates to automatic voice calls.

## GitHub Actions

The repository includes a CI workflow that runs on every push and pull request. It:

- Sets up Python
- Installs dependencies from `requirements.txt`
- Checks Python syntax with `compileall`
- Imports the main modules as a smoke test

This keeps the project lightweight while still catching broken imports and syntax errors before changes are merged.

## Safety Notes

- Do not commit real Twilio credentials.
- Verify all emergency phone numbers before disabling demo mode.
- Twilio trial accounts can only contact verified destination numbers.
- This project is a demonstration system and should be tested thoroughly before any real-world emergency use.

## License

Add your preferred license before distributing this project publicly.
