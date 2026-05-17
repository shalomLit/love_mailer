import math
import smtplib
from zoneinfo import ZoneInfo

import requests
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_weather():
    api_key = os.getenv("WEATHER_API_KEY")

    url = f"https://api.openweathermap.org/data/2.5/forecast?q=Lod,IL&appid={api_key}&units=metric&lang=he"

    response = requests.get(url)
    data = response.json()

    israel_tz = ZoneInfo("Asia/Jerusalem")

    today_israel = datetime.now(israel_tz).date()

    temps = []
    descriptions = []

    for item in data["list"]:
        # הזמן מגיע ב-UTC
        utc_time = datetime.fromtimestamp(item["dt"], tz=ZoneInfo("UTC"))

        # המרה לשעון ישראל
        israel_time = utc_time.astimezone(israel_tz)

        # רק של היום בישראל
        if israel_time.date() != today_israel:
            continue

        # רק בין 10:00 ל-17:00
        if 9 <= israel_time.hour <= 18:
            temps.append(item["main"]["temp_max"])
            descriptions.append(item["weather"][0]["description"])

            print(
                f"שעה: {israel_time.strftime('%H:%M')} | "
                f"טמפ': {item['main']['temp_max']}°C"
            )

    if not temps:
        return None, None

    max_temp = math.ceil(max(temps))
    description = descriptions[0]

    return max_temp, description


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
    - Clothing recommendation must explicitly mention:
    whether children should wear a short-sleeve shirt or a long-sleeve shirt during the day.

    - Be decisive and specific.
      Do not give vague recommendations like "depending on sensitivity to cold".
      - Do not include any recommendations about shoes or footwear.

    - Example:
      "לילדים מומלצת חולצה קצרה."
      or
      "לילדים מומלצת חולצה ארוכה דקה בשעות הבוקר."
          Include what to wear during daytime hours.
        "don't mention evening recommendation, only for morning and during the day.

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

- The message MUST end with the exact text below on a new separate line:
"שיהיה יום טוב"
    """

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


def send_email(message):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    receivers = [
        "shdover0@gmail.com",
    ]

    msg = MIMEText(message, "plain", "utf-8")
    msg["Subject"] = "בוקר טוב – תחזית מזג אוויר להיום"
    msg["From"] = sender
    msg["To"] = ", ".join(receivers)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg, from_addr=sender, to_addrs=receivers)


if __name__ == "__main__":
    message = generate_message()
    send_email(message)
    print("Email sent successfully")
