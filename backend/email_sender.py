import smtplib
from email.message import EmailMessage

def send_complaint_email(
    receiver_email,
    subject,
    body,
    image_path=None
):
    msg = EmailMessage()

    msg["Subject"] = subject
    msg["From"] = "sinha.aryan5643@gmail.com"
    msg["To"] = receiver_email

    msg.set_content(body)

    if image_path:
        with open(image_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="image",
                subtype="jpeg",
                filename="complaint.jpg"
            )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(
            "sinha.aryan5643@gmail.com",
            "ylng lpiq jvao eptq"
        )
        smtp.send_message(msg)