# Smart Accident Web Dashboard

This is a zero-install web dashboard for the accident detection and emergency escalation demo.

## Live Hosted Dashboard

🌐 **Vercel Link**: [https://accident-detection-response-system.vercel.app](https://accident-detection-response-system.vercel.app)

## Local Run

```powershell
python web_dashboard.py
```

Then open:

```text
http://127.0.0.1:8080
```

Use this command if you do not want Python to open a browser automatically:

```powershell
python web_dashboard.py --no-browser
```

## Modes

- Demo mode is enabled by default, so SMS and call delivery are simulated safely.
- Turn demo mode off from the Settings panel only after `.env` contains valid Twilio values.
- The existing Tkinter app is still available in `accident_ui.py`.

## Dashboard Features

- Live accident event panel
- 30-second driver response timer
- SMS escalation workflow
- 15-second acknowledgement timer
- Automatic call escalation
- Editable vehicle and location
- Editable contact rows
- Contact-level SMS/call status
- Twilio readiness badge
- Live emergency workflow log
