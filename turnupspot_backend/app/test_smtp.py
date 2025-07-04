import smtplib

server = smtplib.SMTP("smtp-mail.outlook.com", 587)
server.starttls()
server.login("support@turnupspot.com", "ccrpznjdwjvmknlk")
server.sendmail(
    "support@turnupspot.com",
    "kamar3deen@gmail.com",
    "Subject: Test\n\nThis is a test email."
)
server.quit()