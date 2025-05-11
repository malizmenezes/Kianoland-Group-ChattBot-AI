from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
from dialogflow_integration import detect_intent
import discord
from discord.ext import commands
import asyncio
import threading
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Validasi token penting
if not os.getenv("DISCORD_TOKEN"):
    raise ValueError("DISCORD_TOKEN tidak ditemukan di .env")

if not os.getenv("TELEGRAM_TOKEN"):
    raise ValueError("TELEGRAM_TOKEN tidak ditemukan di .env")

if not os.getenv("DIALOGFLOW_PROJECT_ID"):
    raise ValueError("DIALOGFLOW_PROJECT_ID tidak ditemukan di .env")

if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS tidak ditemukan di .env")

if not os.getenv("TELEGRAM_WEBHOOK_URL"):
    raise ValueError("TELEGRAM_WEBHOOK_URL tidak ditemukan di .env")

# 🚀 Initialize FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    allow_credentials=True
)

# 🛠️ Configurations from .env
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEDICATED_CHANNEL_ID = int(os.getenv("DEDICATED_CHANNEL_ID"))
DIALOGFLOW_PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")
BOT_PREFIXES = ('!', '/', '$')

# Initialize Discord Client
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
discord_bot = commands.Bot(command_prefix=BOT_PREFIXES, intents=intents)

# Discord Models
class DiscordMessage(BaseModel):
    content: str
    channel_id: int
    author: dict

# Discord Bot Functions
def run_discord_bot():
    @discord_bot.event
    async def on_ready():
        await discord_bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"#{discord_bot.get_channel(DEDICATED_CHANNEL_ID).name}"
            )
        )
        print(f'Logged in as {discord_bot.user} (ID: {discord_bot.user.id})')
        
        # Send guide message to dedicated channel
        channel = discord_bot.get_channel(DEDICATED_CHANNEL_ID)
        async for msg in channel.history(limit=5):
            if msg.author == discord_bot.user and "PANDUAN" in msg.content:
                break
        else:
            await channel.send(
                "📌 **PANDUAN PENGGUNAAN**\n"
                "1. Ketik `!info` untuk melihat promo properti\n"
                "2. Gunakan `!konsul [pertanyaan]` untuk bantuan\n"
                "3. Bot hanya aktif di channel ini"
            )

    @discord_bot.event
    async def on_message(message):
        # Ignore messages from other bots
        if message.author.bot:
            return

        # Handle messages in dedicated channel
        if message.channel.id == DEDICATED_CHANNEL_ID:
            # Process commands with prefixes
            if message.content.startswith(BOT_PREFIXES):
                await discord_bot.process_commands(message)
                await asyncio.sleep(3)
                try:
                    await message.delete()
                except:
                    pass
            # Process normal messages
            else:
                result = detect_intent(message.content, DIALOGFLOW_PROJECT_ID)
                await message.reply(result['discord'])  # Hanya kirim bagian discord
        
        # Handle mentions in other channels
        elif discord_bot.user.mentioned_in(message):
            await message.reply(
                f"💡 Silakan gunakan <#{DEDICATED_CHANNEL_ID}> untuk berinteraksi dengan bot.\n"
                "Saya tidak akan merespon di channel ini.",
                delete_after=15
            )

    # Custom commands
    @discord_bot.command()
    async def proyek(ctx):
        result = detect_intent("daftar proyek", DIALOGFLOW_PROJECT_ID)
        await ctx.send(result['discord'])  # Hanya kirim bagian discord
        
    @discord_bot.command()
    async def info(ctx):
        """Get property information"""
        response = detect_intent("info properti", DIALOGFLOW_PROJECT_ID)
        await ctx.send(response)

    @discord_bot.command()
    async def konsul(ctx, *, question: str):
        """Create consultation thread"""
        thread = await ctx.channel.create_thread(
            name=f"Konsul-{ctx.author.display_name}",
            type=discord.ChannelType.private_thread,
            reason=f"Konsultasi properti oleh {ctx.author}"
        )
        response = detect_intent(question, DIALOGFLOW_PROJECT_ID)
        await thread.send(
            f"🛎️ Konsultasi dimulai oleh {ctx.author.mention}!\n"
            f"**Pertanyaan:** {question}\n\n"
            f"**Jawaban:** {response}"
        )
        await ctx.message.delete()

    discord_bot.run(DISCORD_TOKEN)

# Start Discord bot in separate thread
@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=run_discord_bot, daemon=True)
    thread.start()

# REST API Endpoints
@app.post("/discord-webhook")
async def discord_webhook(message: DiscordMessage):
    try:
        if message.author.get("bot", False):
            return {"status": "ignored"}
        
        result = detect_intent(message.content, DIALOGFLOW_PROJECT_ID)
        channel = discord_bot.get_channel(message.channel_id)
        await channel.send(result['discord'])  # Hanya kirim bagian discord
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(400, str(e))

# 🛠️ Konfigurasi Telegram
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

async def send_telegram_message(chat_id: int, text: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        )

# 📱 Endpoint untuk UI web / chat
class ChatRequest(BaseModel):
    user_input: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        result = detect_intent(request.user_input, DIALOGFLOW_PROJECT_ID)
        return {
            "response": {
                "raw": result['raw'],
                "formatted": result['web']
            }
        }
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/telegram-webhook")
async def telegram_webhook(request: Request):
    update = await request.json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"].get("text", "")
        
        result = detect_intent(text, DIALOGFLOW_PROJECT_ID)
        await send_telegram_message(chat_id, result['telegram'])
    
    return {"ok": True}

# 📢 (Optional) set webhook secara otomatis saat startup
@app.on_event("startup")
async def on_startup():
    # Ganti dengan URL publik (ngrok atau domain Anda)
    webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL")
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{TELEGRAM_API_URL}/setWebhook",
            json={"url": webhook_url}
        )
        print("setWebhook result:", res.json())

