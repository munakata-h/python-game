import subprocess
import sys
import os
import tkinter as tk
from tkinter import font
import google.generativeai as genai
import threading

# --- 設定: ステージ構成のリクエスト ---
# 今後ゲームが増えたら、このリストに要素を追加するだけでOKです
STAGES = [
    {"id": 1, "file": "game001.py", "title": "STAGE 1", "msg": "【第１ステージ】\n\n新しい冒険の始まりだ！ゴールを目指して頑張ろう！"},
    {"id": 2, "file": "game002.py", "title": "STAGE 2", "msg": "【第２ステージ】\n\nインベーダー戦！タコお化けを倒せ！"},
    {"id": 3, "file": "game003.py", "title": "STAGE 3", "msg": "【第３ステージ】\n\n君こそパックマン！敵に捕まらないよう食べつくせ！"}, 
    # {"id": 3, "file": "game003.py", "title": "STAGE 3", "msg": "新しい冒険の始まりだ！"}, # 例
]

# --- 1. AI実況取得関数 ---
def get_ai_briefing():
    prompt = (
        "あなたはゲームの進行役です。以下の2点を短く親しみやすい口調で教えてください。\n"
        "1. 明日の埼玉県のアバウトな天気予報\n"
        "2. 本日の日本の重大ニュースを1つ\n"
        "最後に『それでは次のステージを開始します！』と締めくくってください。"
    )
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"通信エラーのため、予備情報で進行します。\n(エラー内容: {e})"

# --- 2. 共通ポップアップクラス ---
class GamePopup:
    def __init__(self, title, width=1200, height=800):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#f0f0f0")
        
        # 画面中央配置
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        self.custom_font = font.Font(family="Meiryo", size=20, weight="bold")
        self.btn_font = font.Font(family="Meiryo", size=18, weight="bold")

    def show_simple(self, message):
        """通常のメッセージ表示"""
        tk.Label(self.root, text=message, font=self.custom_font, wraplength=1000, 
                 bg="#f0f0f0", pady=100).pack(expand=True)
        tk.Button(self.root, text="OK", font=self.btn_font, command=self.root.destroy, 
                  bg="#0078d7", fg="white", padx=60, pady=20).pack(pady=50)
        self.root.mainloop()

    def show_ai_transition(self, score):
        """AI実況付きの遷移画面"""
        label_text = tk.StringVar()
        label_text.set(f"【 ステージ終了 】\n\n現在のスコア： {score} 点\n\nAIナビゲーターが最新情報をスキャン中...")
        
        label = tk.Label(self.root, textvariable=label_text, font=self.custom_font, 
                         wraplength=1000, justify="left", bg="#f0f0f0", padx=50, pady=50)
        label.pack(expand=True, fill="both")

        btn = tk.Button(self.root, text="AIスキャン中...", font=self.btn_font, state="disabled",
                        command=self.root.destroy, bg="#cccccc", fg="white", padx=40, pady=20)
        btn.pack(pady=40)

        def fetch():
            ai_msg = get_ai_briefing()
            self.root.after(0, lambda: label_text.set(ai_msg))
            self.root.after(0, lambda: btn.config(state="normal", bg="#0078d7", text="実況を聞いて次へ進む"))

        threading.Thread(target=fetch, daemon=True).start()
        self.root.mainloop()

# --- 3. ユーティリティ ---
def get_current_score():
    if os.path.exists("score.txt"):
        with open("score.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    return "0"

def run_script(script_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, script_name)
    if os.path.exists(script_path):
        subprocess.call([sys.executable, script_path])

# --- 4. メイン処理 ---
def main():
    # APIキー読み込み
    if os.path.exists("API_KEY.txt"):
        with open("API_KEY.txt", "r", encoding="utf-8") as f:
            genai.configure(api_key=f.read().strip())
    else:
        print("API_KEY.txtが見つかりません。")
        return

    # 全ステージをループで実行
    for i, stage in enumerate(STAGES):
        # 開始ポップアップ
        GamePopup(stage["title"]).show_simple(stage["msg"])
        
        # ゲーム本編実行
        run_script(stage["file"])
        
        # 最終ステージ以外はAI実況ポップアップを表示
        if i < len(STAGES) - 1:
            GamePopup("AI実況ナビゲーター").show_ai_transition(get_current_score())

    # 全クリ後の最終リザルト
    GamePopup("ALL CLEAR!").show_simple(f"おめでとう！！\n全ミッションクリア！\n\n最終スコア: {get_current_score()} 点")
    sys.exit()

if __name__ == "__main__":
    main()