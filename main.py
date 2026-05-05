import smtplib
from datetime import datetime
import os
from email.mime.text import MIMEText

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_message():
    day_of_week = datetime.now().strftime("%A")  # e.g. Monday, Wednesday

    prompt = f"""
כתוב הודעה קצרה, אישית וחמה לאשתי שרי.

רקע עובדתי:
- יש לנו 5 ילדים: בת בכורה ו־4 בנים
- אחד הילדים בן 3 עם אתגרים התפתחותיים שמוסיפים עומס יומיומי
- שרי עובדת קשה מאוד ומנהלת בית עמוס

היום הוא יום {day_of_week}.

הנחיות:
- אל תשתמש בשפה רפואית או אבחנתית
- במקום לתאר את הילד, התייחס רק באופן כללי ל"אתגרים" או "עומס"
- אל תיכנס לפרטים על הילדים
- אל תמציא אירועים
- אל תציע פעולות או פתרונות
- אם זה יום רביעי: אפשר לציין בעדינות שזה יום עמוס במיוחד עבורה
- עד 2–3 שורות
- סגנון טבעי, אנושי, עדין ולא קיטשי
- מותר טון אוהב ואינטימי, אבל לא בוטה או מיני מפורש
- אפשר להביע משיכה בצורה עדינה ומכבדת
כתוב הודעה בעברית.
חלק אותה לפסקאות.
השתמש בירידת שורה בין כל פסקה.
אל תכתוב הכל בשורה אחת.
"""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


def send_email(message):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    receiver = "shdover0@gmail.com"

    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = "💛 הודעה קטנה ממני אלייך"
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)


if __name__ == "__main__":
    message = generate_message()
    send_email(message)
    print("Email sent successfully")