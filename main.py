# main.py
import discord
import os
import asyncio
from discord.ext import commands
from discord.ext.voice_recv import VoiceRecvClient, WaveSink
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True # メッセージコンテンツインテントを有効にする
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect(cls=VoiceRecvClient)
        await ctx.send("VCに接続しました")
    else:
        await ctx.send("先にVCに参加してください")

@bot.command()
async def record(ctx, duration: int = 10):
    vc = ctx.voice_client
    if not isinstance(vc, VoiceRecvClient):
        await ctx.send("VCに接続していません。`!join` を使ってください")
        return

    os.makedirs("recordings", exist_ok=True)
    filename = f"recordings/recorded.wav"
    sink = WaveSink(filename)
    vc.listen(sink)

    await ctx.send(f"{duration}秒間録音中...")
    await asyncio.sleep(duration)

    vc.stop_listening()
    await ctx.send(f"録音完了: `{filename}` に保存しました")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("VCから切断しました")
    else:
        await ctx.send("VCに接続していません")

bot.run(TOKEN)
