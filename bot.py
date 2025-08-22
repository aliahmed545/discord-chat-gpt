import discord
import os
import asyncio
import zipfile
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def convert(ctx):
    if not ctx.message.attachments:
        await ctx.send("❌ أرسل ملف فيديو أو zip مع الأمر.")
        return

    attachment = ctx.message.attachments[0]
    filename = attachment.filename.lower()

    input_file = f"input_{attachment.filename}"
    output_file = "output.mov"
    output_zip = "output.zip"

    # نزّل الملف
    await attachment.save(input_file)

    # لو كان الملف فيديو مباشر
    if filename.endswith((".mp4", ".mov", ".mkv", ".avi")):
        cmd = f'ffmpeg -y -itsscale 2 -i "{input_file}" -c:v copy -c:a copy "{output_file}"'
        process = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()

        if os.path.exists(output_file):
            await ctx.send("✅ تم التحويل:", file=discord.File(output_file))
        else:
            await ctx.send("❌ خطأ أثناء التحويل.")

    # لو الملف zip
    elif filename.endswith(".zip"):
        extract_folder = "extracted"
        output_folder = "processed"
        os.makedirs(extract_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)

        with zipfile.ZipFile(input_file, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

        for file in os.listdir(extract_folder):
            if file.lower().endswith((".mp4", ".mov", ".mkv", ".avi")):
                input_path = os.path.join(extract_folder, file)
                output_path = os.path.join(output_folder, file)

                cmd = f'ffmpeg -y -itsscale 2 -i "{input_path}" -c:v copy -c:a copy "{output_path}"'
                process = await asyncio.create_subprocess_shell(
                    cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()

        # اضغط النتائج في zip
        with zipfile.ZipFile(output_zip, 'w') as zipf:
            for file in os.listdir(output_folder):
                zipf.write(os.path.join(output_folder, file), file)

        if os.path.exists(output_zip):
            await ctx.send("✅ تم التحويل:", file=discord.File(output_zip))
        else:
            await ctx.send("❌ خطأ أثناء إنشاء ملف zip.")

        # تنظيف
        for folder in [extract_folder, output_folder]:
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    os.remove(os.path.join(folder, f))
                os.rmdir(folder)

    else:
        await ctx.send("❌ هذا النوع من الملفات غير مدعوم. أرسل فيديو أو ملف zip.")

    # تنظيف
    for f in [input_file, output_file, output_zip]:
        if os.path.exists(f):
            os.remove(f)

bot.run(os.getenv("TOKEN"))
