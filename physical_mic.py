import asyncio

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import sys
import os
import datetime

# load_voice_to_txtとsummarizerは外部モジュールなのでimportは残す
import transcribe_whisper
import summarizer

# --- ここからクラス定義に修正 ---
class AudioRecorder:
    def __init__(self, samplerate=44100, channels=1):
        self.samplerate = samplerate
        self.channels = channels
        self.audio_data_buffer = []  # インスタンス変数としてデータを保持
        self.is_recording = False    # インスタンス変数として録音状態を保持

    def callback(self, indata, frames, time, status):
        """
        オーディオブロックごとに呼び出されます。
        このメソッドはクラスのインスタンス変数にアクセスします。
        """
        if status:
            print(status, file=sys.stderr)
        if self.is_recording: # self. を付けてインスタンス変数にアクセス
            self.audio_data_buffer.append(indata.copy()) # self. を付けてインスタンス変数にアクセス

    def record_audio_by_mic(self): # 引数からis_recording, audio_data_bufferを削除
        """
        マイクから録音，手動停止
        """
        # ここはクラスのメソッドなので、インスタンス変数 self.is_recording と self.audio_data_buffer を使用
        self.is_recording = True
        self.audio_data_buffer = [] # 録音開始時にバッファをクリア

        # 日時設定とディレクトリ設定はそのまま
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = "recordings"
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.join(output_dir, f"record_{now}.wav")

        print(f"マイクからの連続録音を開始します（サンプリングレート: {self.samplerate} Hz）...")
        print(f"録音は '{output_filename}' に保存されます。")
        print("録音を停止するには **Enterキー** を押してください...")

        try:
            # callbackに self.callback を渡すことで、インスタンスのメソッドが呼び出される
            with sd.InputStream(samplerate=self.samplerate, channels=self.channels, dtype='int16', callback=self.callback):
                input() # ユーザーがEnterキーを押すのを待つ

            self.is_recording = False # 録音終了フラグを設定
            print("録音を停止中...")

            if self.audio_data_buffer:
                final_audio_data = np.concatenate(self.audio_data_buffer, axis=0)
                write(output_filename, self.samplerate, final_audio_data)
                print(f"音声は正常に '{output_filename}' に保存されました。")
            else:
                print("音声データは録音されませんでした。")

        except KeyboardInterrupt:
            print("\nユーザーによって録音が中断されました（Ctrl+C）。")
        except Exception as e:
            print(f"エラーが発生しました: {e}", file=sys.stderr)
            print("マイクが接続されており、動作していること、および必要なアクセス許可があることを確認してください。")
        finally:
            self.is_recording = False # 確実にフラグをリセット

            # 文字起こしと要約の処理
            try:
                print("文字起こしを開始します (ローカルWhisperモデルを使用)...")
                # transcribe_audio_localがasync defならawaitが必要
                # しかし、mic.pyのrecord_audio_by_micがasync defではないので、
                # ここでは同期的に呼び出される前提、または別途asyncio.runが必要
                # 前回のRuntimeWarningからすると、ここで await が抜けている可能性が高い
                transcription = asyncio.run(transcribe_whisper.transcribe_audio_local(output_filename)) # <- ここに await が必要なら追加
                transcription_filename_path = output_filename.replace(".wav", ".txt")
                try:
                    with open(transcription_filename_path, "w", encoding="utf-8") as f:
                        f.write(transcription)
                    print(f"文字起こし結果をローカルに保存しました: {transcription_filename_path}")
                    # summarizer.summarize が文字列を返すことを確認
                    summarizer.summarize(transcription, transcription_filename_path)
                except Exception as file_error:
                    print(f"文字起こし結果のファイル保存中にエラーが発生しました: {file_error}")
                    print(f"⚠️ 文字起こし結果のファイル保存に失敗しました: {file_error}")
            except ImportError:
                print("ImportError: Whisper or PyTorch not installed.")
            except Exception as e:
                print(f"文字起こしエラー: {e}")

# クラスの外にrecord_audio_by_mic関数はもう必要ありません
# main.py からは AudioRecorderのインスタンスを作成して呼び出します