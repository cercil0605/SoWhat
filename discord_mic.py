import discord
import os
from discord.ext import commands
from discord.ext.voice_recv import VoiceRecvClient, WaveSink
from dotenv import load_dotenv
import datetime
import transcribe_whisper

import summarizer

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
        # 文字起こし
        try:
            await ctx.send("文字起こしを開始します (ローカルWhisperモデルを使用)...")
            transcription = await transcribe_whisper.transcribe_audio_local(bot.filename)
            transcription_filename_path = bot.filename.replace(".wav", ".txt")
            try:
                with open(transcription_filename_path, "w", encoding="utf-8") as f:
                    f.write(transcription)
                print(f"文字起こし結果をローカルに保存しました: {transcription_filename_path}")
                summarizer.summarize(transcription, transcription_filename_path)
                await ctx.send("要約をMarkdownファイルとして送信します。")
                await ctx.send(file=discord.File(transcription_filename_path))
            except Exception as file_error:
                print(f"文字起こし結果のファイル保存中にエラーが発生しました: {file_error}")
                await ctx.send(f"⚠️ 文字起こし結果のファイル保存に失敗しました: {file_error}")
        except ImportError:
            await ctx.send(
                "文字起こしライブラリがインストールされていません。`pip install torch torchaudio` を実行してください。")
            print("ImportError: Whisper or PyTorch not installed.")
        except Exception as e:
            await ctx.send(f"文字起こし中にエラーが発生しました: {e}")
            print(f"文字起こしエラー: {e}")

        bot.sink = None
        bot.filename = None
    else:
        await ctx.send("録音していません")

# bot.run(TOKEN)