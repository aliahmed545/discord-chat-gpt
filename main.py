import discord
import openai
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if "#سؤال" not in message.content:
        return

    prompt = message.content.replace("#سؤال", "").strip()

    if not prompt:
        await message.channel.send("يرجى كتابة السؤال بعد #سؤال")
        return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أجب على السؤال باختصار وباللغة العربية."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content

        embed = discord.Embed(
            title="📌 إجابة GPT",
            description=answer,
            color=discord.Color.purple()
        )
        embed.set_footer(text="تم الرد على سؤالك باستخدام GPT-3.5")
        await message.channel.send(embed=embed)

    except Exception as e:
        await message.channel.send("حدث خطأ أثناء معالجة سؤالك.")
        print(f"GPT Error: {e}")

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
