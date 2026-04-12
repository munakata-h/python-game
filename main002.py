import subprocess
import sys
import os
import time
import tkinter as tk
from tkinter import font
import google.generativeai as genai
import threading

# --- 1. AI実況取得関数 ---
def get_ai_briefing():
    prompt = (
        "あなたはゲームの進行役です。以下の2点を短く親しみやすい口調で教えてください。\n"
        "1. 明日の埼玉県のアバウトな天気予報\n"
        "2. 本日の日本の重大ニュースを1つ\n"
        "最後に『それでは第2ステージ、インベーダー戦を開始します！』と締めくくってください。"
    )
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"通信エラーのため、予備情報で進行します。\n(エラー内容: {e})"

# --- 2. 待機と書き換えができる特大ポップアップ ---
def show_transition_popup(score_val):
    popup = tk.Tk()
    popup.title("AI実況ナビゲーター")
    
    # サイズ：1200x800
    window_width, window_height = 1200, 800
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    cp_x = int(screen_width/2 - window_width/2)
    cp_y = int(screen_height/2 - window_height/2)
    popup.geometry(f"{window_width}x{window_height}+{cp_x}+{cp_y}")
    popup.attributes("-topmost", True)
    popup.configure(bg="#f0f0f0")

    custom_font = font.Font(family="Meiryo", size=20, weight="bold")
    
    # メッセージラベル（最初はスコアを表示）
    label_text = tk.StringVar()
    label_text.set(f"【 第１ステージ終了 】\n\n獲得スコア： {score_val} 点\n\n現在、AIナビゲーターが最新情報をスキャンしています...\nそのまま少しお待ちください。")
    
    label = tk.Label(popup, textvariable=label_text, font=custom_font, wraplength=1000, 
                    justify="left", bg="#f0f0f0", padx=50, pady=50)
    label.pack(expand=True, fill="both")

    # ボタン（最初は無効）
    btn_font = font.Font(family="Meiryo", size=18, weight="bold")
    btn = tk.Button(popup, text="AIスキャン中...", font=btn_font, state="disabled",
                   command=popup.destroy, bg="#cccccc", fg="white", padx=40, pady=20)
    btn.pack(pady=40)

    # 裏でAI処理を走らせる
    def fetch_and_update():
        ai_response = get_ai_briefing()
        # メインスレッドでUIを更新
        popup.after(0, lambda: label_text.set(ai_response))
        popup.after(0, lambda: btn.config(state="normal", bg="#0078d7", text="実況を聞いて次へ進む"))

    threading.Thread(target=fetch_and_update, daemon=True).start()
    popup.mainloop()

# 通常のポップアップ用
def show_simple_popup(title, message):
    popup = tk.Tk()
    popup.title(title)
    popup.geometry("1200x800")
    popup.attributes("-topmost", True)
    
    # 画面中央寄せ
    popup.update_idletasks()
    x = (popup.winfo_screenwidth() // 2) - (1200 // 2)
    y = (popup.winfo_screenheight() // 2) - (800 // 2)
    popup.geometry(f"1200x800+{x}+{y}")

    custom_font = font.Font(family="Meiryo", size=20, weight="bold")
    tk.Label(popup, text=message, font=custom_font, wraplength=1000, pady=100).pack(expand=True)
    tk.Button(popup, text="OK", font=("Meiryo", 18), command=popup.destroy, bg="#0078d7", fg="white", padx=60, pady=20).pack(pady=50)
    popup.mainloop()

# --- 3. スクリプト実行設定 ---
def run_script(script_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, script_name)
    if not os.path.exists(script_path):
        print(f"File not found: {script_name}")
        return False
    try:
        subprocess.call([sys.executable, script_path])
        return True
    except Exception as e:
        print(f"Error running {script_name}: {e}")
        return False

# --- 4. メイン処理 ---
def main():
    # 1. APIキー設定
    key_path = "API_KEY.txt"
    if os.path.exists(key_path):
        with open(key_path, "r", encoding="utf-8") as f:
            API_KEY = f.read().strip()
        genai.configure(api_key=API_KEY)
    else:
        print("API_KEY.txtが見つかりません。")
        return

    # ステージ1開始
    show_simple_popup("STAGE 1", "【第１ステージ】\n\nまずはゴールを目指して頑張ろう！")
    run_script("game001.py")

    # スコア読み込み
    score_val = "0"
    if os.path.exists("score.txt"):
        with open("score.txt", "r") as f:
            score_val = f.read().strip()

    # スコア表示 ＆ 裏でAI処理
    show_transition_popup(score_val)

    # ステージ2開始
    show_simple_popup("STAGE 2", "【第２ステージ】\n\nいよいよインベーダー戦！お化けを倒せ！")
    run_script("game002.py")

    # 完了
    show_simple_popup("ALL CLEAR!", "おめでとう！！\nすべてのミッションをクリアしたよ！")
    sys.exit()

if __name__ == "__main__":
    main()