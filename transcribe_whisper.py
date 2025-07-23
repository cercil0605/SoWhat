import asyncio
from typing import Literal


async def transcribe_audio_local(file_path: str) -> str:
    return await _transcribe_via_subprocess(file_path, backend="oss-whisper")


async def transcribe_audio_local_by_mlx(file_path: str) -> str:
    return await _transcribe_via_subprocess(file_path, backend="mlx-whisper")


async def _transcribe_via_subprocess(
    file_path: str,
    backend: Literal["oss-whisper", "mlx-whisper"]
) -> str:
    """
    Subprocessで transcribe_worker.py を呼び出し、文字起こしを行う

    Args:
        file_path: 音声ファイルのパス（.wav）
        backend: 'oss-whisper' or 'mlx-whisper'

    Returns:
        文字起こし結果の文字列

    Raises:
        RuntimeError: subprocessが失敗した場合
    """
    output_txt_path = file_path.replace(".wav", ".txt")
    command = [
        "python3",
        "transcribe_worker.py",
        file_path,
        output_txt_path,
        backend
    ]

    print(f"[INFO] Subprocess起動: {' '.join(command)}")
    proc = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(
            f"[ERROR] transcribe_worker.py failed with exit code {proc.returncode}\n"
            f"{stderr.decode(errors='ignore')}"
        )

    print(f"[DEBUG] stdout:\n{stdout.decode(errors='ignore')}")
    print(f"[DEBUG] stderr:\n{stderr.decode(errors='ignore')}")

    try:
        with open(output_txt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise RuntimeError(f"[ERROR] 出力ファイルが見つかりません: {output_txt_path}")
