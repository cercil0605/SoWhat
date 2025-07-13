# whisper_transcriber.py
import asyncio
import whisper

_local_whisper_model = None # モデルをキャッシュするためのグローバル変数

async def transcribe_audio_local(file_path: str, model_name: str = "base") -> str:
    """
    ローカルのWhisperモデルを使用して音声ファイルを文字起こしします。
    """
    global _local_whisper_model
    if _local_whisper_model is None:
        print(f"Whisperモデル '{model_name}' をロード中...")
        # モデルのロードはブロッキングなので、asyncio.to_threadで別スレッドで実行
        _local_whisper_model = await asyncio.to_thread(whisper.load_model, model_name)
        print(f"Whisperモデル '{model_name}' のロードが完了しました。")

    # デバイスの自動検出（Mac向け）
    import torch
    device = "cpu"
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    print(f"Whisperモデルを {device} デバイスで実行します。")

    # 文字起こしはブロッキングなので、asyncio.to_threadで別スレッドで実行
    result = await asyncio.to_thread(
        _local_whisper_model.transcribe,
        file_path,
        language="ja"
    )
    return result["text"]