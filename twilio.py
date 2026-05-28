"""Twilio SMS and call helper for the accident alert system.

This file is intentionally named ``twilio.py`` to match the project request.
Because that shadows the official ``twilio`` SDK package name, this module
uses Twilio's REST API directly with ``requests``.
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

import requests


E164_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")
TWILIO_API_BASE = "https://api.twilio.com/2010-04-01"


def _load_local_env() -> None:
    env_path = Path(__file__).with_name(".env")
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_local_env()


ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "PASTE_YOUR_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "PASTE_YOUR_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "+1XXXXXXXXXX")
DEFAULT_TO_NUMBER = os.getenv("TWILIO_TO_NUMBER", "+91XXXXXXXXXX")
DEFAULT_VOICE_URL = os.getenv("TWILIO_VOICE_URL", "http://demo.twilio.com/docs/voice.xml")
DEFAULT_VOICE_NAME = os.getenv("TWILIO_VOICE_NAME", "Polly.Joanna")
DEFAULT_VOICE_LANGUAGE = os.getenv("TWILIO_VOICE_LANGUAGE", "en-US")
DEFAULT_VOICE_RATE = os.getenv("TWILIO_VOICE_RATE", "85%")


def _is_placeholder(value: str) -> bool:
    return not value or "PASTE_" in value or "XXXXXXXX" in value


def _clean_number(number: str) -> str:
    return re.sub(r"[\s()-]", "", (number or "").strip())


def _valid_e164(number: str) -> bool:
    return bool(E164_PATTERN.fullmatch(_clean_number(number)))


def build_emergency_sms(vehicle_number: str, location: str, event_time: str) -> str:
    return (
        "Accident detected.\n"
        f"Vehicle: {vehicle_number}\n"
        f"Location: {location}\n"
        f"Time: {event_time}\n"
        "Please respond immediately."
    )


def build_voice_message(vehicle_number: str, location: str, event_time: str) -> str:
    return (
        "Emergency alert. "
        f"Accident detected for vehicle {vehicle_number}. "
        f"Location {location}. "
        f"Time {event_time}. "
        "Please respond immediately."
    )


class TwilioService:
    """REST wrapper for Twilio SMS and voice calls with strong debug logging."""

    def __init__(
        self,
        account_sid: str = ACCOUNT_SID,
        auth_token: str = AUTH_TOKEN,
        from_number: str = TWILIO_NUMBER,
    ):
        self.account_sid = account_sid.strip()
        self.auth_token = auth_token.strip()
        self.from_number = _clean_number(from_number)

    def validate_configuration(self, to_number: str | None = None) -> list[str]:
        issues: list[str] = []
        target_number = _clean_number(to_number or DEFAULT_TO_NUMBER)

        if _is_placeholder(self.account_sid):
            issues.append("TWILIO_ACCOUNT_SID is missing or still a placeholder.")
        elif not self.account_sid.startswith("AC"):
            issues.append("TWILIO_ACCOUNT_SID should start with 'AC'.")

        if _is_placeholder(self.auth_token):
            issues.append("TWILIO_AUTH_TOKEN is missing or still a placeholder.")

        if _is_placeholder(self.from_number):
            issues.append("TWILIO_FROM_NUMBER is missing or still a placeholder.")
        elif not _valid_e164(self.from_number):
            issues.append("TWILIO_FROM_NUMBER must be in E.164 format, for example +14155552671.")

        if _is_placeholder(target_number):
            issues.append("Destination number is missing or still a placeholder.")
        elif not _valid_e164(target_number):
            issues.append("Destination number must be in E.164 format, for example +919876543210.")

        return issues

    def _request(
        self,
        endpoint: str,
        payload: dict[str, str],
    ) -> dict[str, Any]:
        url = f"{TWILIO_API_BASE}/Accounts/{self.account_sid}/{endpoint}"
        debug: dict[str, Any] = {
            "ok": False,
            "status": "failed",
            "sid": "",
            "error_code": "",
            "error_message": "",
            "more_info": "",
            "http_status": "",
            "request_url": url,
            "payload_preview": {
                key: value if key != "Body" else value[:120]
                for key, value in payload.items()
                if key not in {"Twiml"}
            },
        }

        last_error: requests.RequestException | None = None
        for attempt in range(3):
            try:
                response = requests.post(
                    url,
                    data=payload,
                    auth=(self.account_sid, self.auth_token),
                    timeout=15,
                )
                break
            except requests.RequestException as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(0.8 * (attempt + 1))
        else:
            debug["status"] = "network_error"
            debug["error_message"] = str(last_error)
            return debug

        debug["http_status"] = response.status_code

        try:
            body = response.json()
        except ValueError:
            body = {"message": response.text.strip()}

        if response.ok:
            debug["ok"] = True
            debug["status"] = "sent"
            debug["sid"] = body.get("sid", "")
            return debug

        debug["status"] = "twilio_error"
        debug["error_code"] = str(body.get("code", ""))
        debug["error_message"] = body.get("message", response.text.strip())
        debug["more_info"] = body.get("more_info", "")
        return debug

    def send_sms(self, message: str, to_number: str = DEFAULT_TO_NUMBER) -> dict[str, Any]:
        to_number = _clean_number(to_number)
        validation_errors = self.validate_configuration(to_number)
        if validation_errors:
            return {
                "ok": False,
                "status": "invalid_configuration",
                "sid": "",
                "error_code": "",
                "error_message": " | ".join(validation_errors),
                "more_info": (
                    "For a Twilio trial account, the destination number must also be verified "
                    "inside the Twilio console."
                ),
                "http_status": "",
                "request_url": "",
            }

        return self._request(
            "Messages.json",
            {
                "Body": message.strip(),
                "From": self.from_number,
                "To": to_number,
            },
        )

    def make_call(
        self,
        spoken_message: str,
        to_number: str = DEFAULT_TO_NUMBER,
        fallback_voice_url: str = DEFAULT_VOICE_URL,
    ) -> dict[str, Any]:
        to_number = _clean_number(to_number)
        validation_errors = self.validate_configuration(to_number)
        if validation_errors:
            return {
                "ok": False,
                "status": "invalid_configuration",
                "sid": "",
                "error_code": "",
                "error_message": " | ".join(validation_errors),
                "more_info": (
                    "For a Twilio trial account, the destination number must also be verified "
                    "inside the Twilio console."
                ),
                "http_status": "",
                "request_url": "",
            }

        twiml = (
            "<Response>"
            f"<Say voice='{escape(DEFAULT_VOICE_NAME)}' language='{escape(DEFAULT_VOICE_LANGUAGE)}'>"
            f"<prosody rate='{escape(DEFAULT_VOICE_RATE)}'>{escape(spoken_message.strip())}</prosody>"
            "</Say>"
            "</Response>"
        )
        payload = {
            "From": self.from_number,
            "To": to_number,
            "Twiml": twiml,
        }

        # Twilio ignores Twiml if both Twiml and Url are provided.
        # Only fall back to a hosted URL when no inline TwiML is supplied.
        if fallback_voice_url and not spoken_message.strip():
            payload["Url"] = fallback_voice_url

        return self._request("Calls.json", payload)


def print_result(label: str, result: dict[str, Any]) -> None:
    print(f"{label}: {'SUCCESS' if result.get('ok') else 'FAILED'}")
    if result.get("sid"):
        print(f"Message SID: {result['sid']}")
    if result.get("http_status"):
        print(f"HTTP Status: {result['http_status']}")
    if result.get("error_code"):
        print(f"Twilio Error Code: {result['error_code']}")
    if result.get("error_message"):
        print(f"Error: {result['error_message']}")
    if result.get("more_info"):
        print(f"More Info: {result['more_info']}")
    if result.get("request_url"):
        print(f"Request URL: {result['request_url']}")


def test_sms(
    to_number: str = DEFAULT_TO_NUMBER,
    message: str = "Twilio SMS test from Accident Alert System.",
) -> dict[str, Any]:
    service = TwilioService()
    print("Running Twilio SMS test...")
    print(f"From Number: {service.from_number}")
    print(f"To Number: {_clean_number(to_number)}")
    result = service.send_sms(message, to_number)
    print_result("SMS", result)
    return result


def test_call(
    to_number: str = DEFAULT_TO_NUMBER,
    message: str = "Emergency alert. This is a Twilio voice call test from the Accident Alert System.",
) -> dict[str, Any]:
    service = TwilioService()
    print("Running Twilio voice call test...")
    print(f"From Number: {service.from_number}")
    print(f"To Number: {_clean_number(to_number)}")
    result = service.make_call(message, to_number)
    print_result("CALL", result)
    return result


if __name__ == "__main__":
    test_sms()
