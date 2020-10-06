from flask_mail import Mail, Message
mail = Mail()
def send_email(to_email, subject, body):
  msg = Message(subject, recipients=[to_email])
  msg.html = body
  mail.send(msg)