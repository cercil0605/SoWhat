import discord_mic
import physical_mic # mic.pyがAudioRecorderクラスを持つようになる

def main():
    """
    メイン関数
    """
    while True:
        choice = input("Discordボットを起動しますか、マイクから録音しますか？ (d/m/exit): ").lower()
        if choice == 'd':
            # discord_vc.pyからbotとTOKENを直接インポート
            discord_mic.bot.run(discord_mic.TOKEN)
            # bot.run() は通常、プログラムをブロックし続けるので、
            # ここでbreakすると、ボットが終了した場合にのみプログラム全体が終了します。
            # ボットが終了した後に再度選択肢に戻るならbreakは不要ですが、
            # その場合はボット起動中に他の選択肢は選べません。
            # 現状のコードだと、ボットが終了したらプログラムも終了するフロー
            print("Discordボットの実行が終了しました。") # ボットが停止した場合のみ表示
            break # ボットが停止したらメインループを抜ける

        elif choice == 'm':
            # AudioRecorderクラスのインスタンスを作成し、メソッドを呼び出す
            recorder = physical_mic.AudioRecorder(samplerate=44100, channels=1) # チャンネル数は1で試すことを推奨
            recorder.record_audio_by_mic()
            break # 録音が終了したらメインループを抜ける
        elif choice == 'exit':
            print("終了します。")
            break
        else:
            print("無効な選択です。'd', 'm', または 'exit' を入力してください。")

if __name__ == "__main__":
    main()