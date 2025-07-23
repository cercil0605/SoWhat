import sys

import mlx_whisper
import whisper

def main():
    if len(sys.argv) < 3:
        print("Usage: python transcribe_worker.py <audio_path> <output_txt_path>")
        sys.exit(1)

    audio_path = sys.argv[1]
    output_path = sys.argv[2]
    which_whisper = sys.argv[3]

    if which_whisper == "oss-whisper":
        print(f"Loading Whisper model 'large'...")
        model = whisper.load_model("large")
        print("Transcribing...")
        result = model.transcribe(audio_path, language="ja")
        print(f"Transcription written to: {output_path}")
    elif which_whisper == "mlx-whisper":
        print(f"Loading MLX-Whisper model 'large'...")
        result = mlx_whisper.transcribe(audio_path,path_or_hf_repo="mlx-community/whisper-large-v3-mlx")
        print(f"Transcription written to: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result["text"])


if __name__ == "__main__":
    main()
