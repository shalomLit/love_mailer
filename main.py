import smtplib
import requests
import os
from email.mime.text import MIMEText

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from datetime import datetime

from datetime import datetime


def get_weather():
    api_key = os.getenv("WEATHER_API_KEY")

    url = f"https://api.openweathermap.org/data/2.5/forecast?q=Lod,IL&appid={api_key}&units=metric&lang=he"

    response = requests.get(url)
    data = response.json()

    temps = []
    descriptions = []

    today = datetime.now().date()

    for item in data["list"]:
        dt = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
        if dt.date() != today:
            continue

        hour = dt.hour
        if 11 <= hour <= 17:
            temps.append(item["main"]["temp_max"])
            descriptions.append(item["weather"][0]["description"])

    if not temps:
        return None, None

    avg_temp = round(sum(temps) / len(temps))
    description = descriptions[0]

    return avg_temp, description


def generate_message():
    temp, description = get_weather()

    prompt = f"""
    Write a short good morning message in Hebrew.

    Here is today's weather in Lod, Israel:
    Temperature: {temp}°
    Condition: {description}

    Instructions:
    - Use clear structure with 2–3 short paragraphs and line breaks.
    - Do NOT include units like "C". Temperature should appear only as: 20°.

    - The message MUST start exactly with this format (no changes allowed):
    "בוקר טוב,
    
    המזג אוויר היום בלוד הוא - {temp}° עם {description}."

    - First paragraph is ONLY this greeting + weather line.

    - Second paragraph: clothing recommendation for the DAY.
      Include what to wear during daytime hours.

    - IMPORTANT: also include morning vs evening adjustment:
      mention that mornings and evenings may be cooler/warmer and suggest appropriate clothing for those times (e.g. light layer / jacket / long sleeves).

    - Third paragraph (only if relevant): rain, wind, or extreme heat ("שרב").
      If rain is present, explicitly mention it and recommend an umbrella.

    - Tone should be warm but not overly emotional or romantic.
    - Do not use loving or intimate language.
    - Keep it concise, natural, and professional.
    - When suggesting clothing layers, do NOT be overly cautious.
  Assume a normal preference for cool weather.
  It is fine to suggest light layering when appropriate, but do not over-emphasize warmth.
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


def send_email(message):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    receiver = "sarisat770@gmail.com"

    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = "❤בוקר טוב אהובה שלי – תחזית מזג אוויר להיום"
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)


if __name__ == "__main__":
    message = generate_message()
    send_email(message)
    print("Email sent successfully")
