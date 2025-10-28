import asyncio
from email.message import EmailMessage
from pathlib import Path
import smtplib


async def send_email_message(
        subject: str,
        message_text: str,
        file_path: Path,
        sender_email: str,
        sender_password: str,
        receiver_emails: list[str],
        smtp_server_hostname: str,
        smtp_server_port: int
):
    for receiver_email in receiver_emails:
        subject = subject
        body = message_text
        email = EmailMessage()
        email["From"] = sender_email
        email["To"] = receiver_email
        email["Subject"] = subject
        email.set_content(body, subtype="html")

        with open(file_path, "rb") as f:
            email.add_attachment(
                f.read(),
                filename=file_path.name,
                maintype="application",
                subtype=file_path.name.split(".")[-1]
            )
        try:
            with smtplib.SMTP_SSL(host=smtp_server_hostname, port=smtp_server_port) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, email.as_string())
        except Exception as e:
            print(f"Error: {e}")
        await asyncio.sleep(1)
