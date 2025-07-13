# main.py
import discord
import os
import asyncio
from discord.ext import commands
from discord.ext.voice_recv import VoiceRecvClient, WaveSink
from dotenv import load_dotenv
import datetime

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True # メッセージコンテンツインテントを有効にする
bot = commands.Bot(command_prefix="!", intents=intents)
bot.sink = None
bot.filename = None


@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect(cls=VoiceRecvClient)
        await ctx.send("VCに接続しました")
    else:
        await ctx.send("先にVCに参加してください")

@bot.command()
async def record(ctx):
    vc = ctx.voice_client
    if not isinstance(vc, VoiceRecvClient):
        await ctx.send("VCに接続していません。`!join` を使ってください")
        return
    try:
        vc.stop_listening()
        print("Previous listening stopped.")
    except Exception as e:
        print(f"Could not stop previous listening (maybe not listening): {e}")

    os.makedirs("recordings", exist_ok=True)
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs("recordings", exist_ok=True)
    bot.filename = f"recordings/record_{now}.wav"
    bot.sink = WaveSink(bot.filename)
    vc.listen(bot.sink)

    await ctx.send(f"録音中... `!stop` で終了してください")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("VCから切断しました")
    else:
        await ctx.send("VCに接続していません")

@bot.command()
async def stop(ctx):
    vc = ctx.voice_client
    if bot.sink and vc:
        vc.stop_listening()
        await ctx.send(f"録音完了: `{bot.filename}` に保存しました")
        bot.sink = None
        bot.filename = None
    else:
        await ctx.send("録音していません")

bot.run(TOKEN)
