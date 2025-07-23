from google import genai
from dotenv import load_dotenv

load_dotenv()

def summarize(transcription: str, transcription_filename_path: str) -> str:
    """
    与えられたテキストを要約し、ファイルに保存する
    """
    print("要約を開始します...")
    client = genai.Client()
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="以下の会話をマークダウン形式で要約してください．\n" + transcription
        )
        summary_text = response.text
        summary_filename_path = transcription_filename_path.replace(".txt", "_summary.txt")
        with open(summary_filename_path, "w", encoding="utf-8") as summary_file:
            summary_file.write(summary_text)
        print(f"会話の要約をローカルに保存しました: {summary_filename_path}")
        return summary_text
    except Exception as e:
        print(f"要約中にエラーが発生しました: {e}")
        return f"要約中にエラーが発生しました: {e}"

