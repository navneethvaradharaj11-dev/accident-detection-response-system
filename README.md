# Smart Accident Detection & Response System

A compact Python-based demonstration of an end-to-end accident detection and emergency response workflow. The project provides both a browser dashboard and a Tkinter desktop interface to simulate accident events, trigger alarm and escalation timers, and demonstrate SMS/voice notification flows (Twilio integration optional).

Live demo: https://accident-detection-response-system.vercel.app

Highlights

- Lightweight, single-repo demo for presentations and testing
- Browser-based dashboard plus Tkinter desktop UI
- Simulated real-time accident events and timers
- Configurable escalation: driver response → SMS → acknowledgement → automated voice calls
- Twilio REST integration for real SMS and voice calls (optional)
- Demo mode to safely demonstrate behavior without sending real messages

Repository layout

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
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment variables
└── .github/workflows/ci.yml    # CI smoke tests (syntax + imports)
```

Requirements

- Python 3.10+
- Optional: a Twilio account and credentials to send real SMS/voice calls

Install

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Configuration

1. Copy the example environment file and update values:

```bash
cp .env.example .env
# or on Windows (PowerShell)
# copy .env.example .env
```

2. Edit `.env` and provide your Twilio credentials and phone numbers if you want to enable real notifications.

Example (.env)

```text
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_FROM_NUMBER=+14155552671
TWILIO_TO_NUMBER=+919876543210
DASHBOARD_DEMO_MODE=true
```

Important: Do not commit `.env` or any real credentials into source control. This repository intentionally ignores `.env`.

Running the project

Web dashboard (default host: http://127.0.0.1:8080):

```bash
python web_dashboard.py
```

Options:
- Prevent automatic browser open: `python web_dashboard.py --no-browser`
- Use a different port: `python web_dashboard.py --port 8125`

Tkinter desktop dashboard:

```bash
python accident_ui.py
```

Notification modes

- Demo mode (default when credentials are missing): simulates SMS/calls and is safe for demos.
- Live mode: enable real SMS/voice by providing Twilio credentials in `.env` and disabling demo mode in the dashboard.

How the emergency workflow behaves

1. System monitors for events in normal mode.
2. Trigger an accident simulation from the dashboard.
3. Alarm activates; a 30-second driver response timer starts.
4. If the driver confirms safety, the workflow resets.
5. If the timer expires, SMS alerts are sent to configured emergency contacts.
6. A 15-second acknowledgement timer begins for contacts to confirm receipt.
7. If no acknowledgement is received, the system escalates to automated voice calls via Twilio.

CI / Testing

The repository includes a minimal GitHub Actions workflow that runs on push and pull requests. The workflow:

- Installs Python and dependencies
- Runs a syntax check (compileall)
- Imports the main modules as a smoke test

This keeps the CI fast while catching syntax errors and broken imports.

Security & safety notes

- Never commit real Twilio credentials, API keys, or private data to the repository.
- Verify recipient phone numbers and test with demo mode before enabling live notifications.
- This project is a demonstration system only — do not rely on it for real emergency handling without extensive testing, validation, and appropriate infrastructure.

Contributing

Contributions, bug reports, and improvements are welcome. Please open issues or pull requests and describe the change and reasoning. For larger changes, open an issue first to discuss the approach.

License

Add your preferred license to the repository before redistributing or publishing this project publicly.
