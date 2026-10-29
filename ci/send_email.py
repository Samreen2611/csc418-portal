"""Test report email karta hai. Credentials sirf CI secrets / environment variables se aate hain."""
import json
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_report import build_report  # noqa: E402


def make_message(report, sender, recipient):
    status = report["overall_status"].upper()
    sha = report["commit_sha"]

    lines = [
        f"Overall result : {status}",
        f"Repository     : {report['repository']}",
        f"Branch         : {report['branch']}",
        f"Commit         : {sha}",
        f"Pipeline run   : {report['pipeline_run_id']}",
        f"Timestamp      : {report['timestamp']}",
        "",
        f"Total: {report['total']}   Passed: {report['passed']}   Failed: {report['failed']}",
        "",
        "Individual results:",
    ]
    for t in report["tests"]:
        line = f"  [{t['result'].upper()}] {t['name']}"
        if t.get("failure_message"):
            line += f"\n      {t['failure_message'].splitlines()[0]}"
        lines.append(line)
    lines += ["", "Full report attached (test-report.json)."]

    msg = EmailMessage()
    msg["Subject"] = f"[CI {status}] {report['repository']} @ {sha[:7]}"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content("\n".join(lines))
    msg.add_attachment(
        json.dumps(report, indent=2).encode("utf-8"),
        maintype="application",
        subtype="json",
        filename="test-report.json",
    )
    return msg


def main():
    user = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASSWORD")
    to = os.environ.get("EMAIL_TO")
    if not (user and password and to):
        print("EMAIL_USER / EMAIL_PASSWORD / EMAIL_TO secrets missing; email not sent.")
        return 1

    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "465"))

    msg = make_message(build_report(), user, to)
    with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context(), timeout=30) as server:
        server.login(user, password)
        server.send_message(msg)
    print("Email sent to", to)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("Could not send email:", exc)
        sys.exit(1)