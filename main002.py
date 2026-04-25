import subprocess
import sys
import os
import tkinter as tk
from tkinter import font
from google import genai
import threading
import random

# ============================
# 1. スコア管理クラス
# ============================
class ScoreManager:
    def __init__(self, path="score.txt"):
        self.path = path

    def get(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return f.read().strip()
        return "0"

    def set(self, value):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(str(value))


# ============================
# 2. AI実況クラス（キャラ付き）
# ============================
class AINavigator:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)

        # ランダム質問テンプレート（キャラ付き）
        self.prompts = [
            "今日の日本のニュースを250字以内で、ゲーム実況者っぽく面白く紹介してください。",
            "今日の日付を発言した後に、埼玉県の天気を250字以内で、テンション高めに教えてください。",
            "最近話題のテクノロジーを250字以内で、ワクワクする語り口で紹介してください。",
            "面白い雑学を250字以内で、ちょっとした小ネタ風に教えてください。",
            "ゲーム会社の話題を250字以内で、プレイヤーを楽しませる語り口で紹介してください。"
        ]

    # --- スコアに応じた一言（キャラ付き） ---
    def score_comment(self, score):
        score = int(score)

        if score < 100:
            return "おっと！スコアはまだ控えめ！でも大丈夫、ここから大逆転ってやつを見せてくれ！"
        elif score < 200:
            return "いいねいいね〜！そのスコア、かなりノッてきてるよ！このまま突っ走ろう！"
        elif score < 300:
            return "おおっ、キミ相当やるね！この調子なら伝説プレイヤーも夢じゃない！"
        else:
            return "出た！神スコア！キミ、もはやゲームの精霊に愛されてるよ！"

    # --- AI実況本体 ---
    def get_briefing(self, score):
        # ① スコアに応じた一言
        comment = self.score_comment(score)

        # ② ランダム質問テンプレート
        question = random.choice(self.prompts)

        # ③ 最後の締め
        closing = (
            "最後に、ゲームの進行役としてひと言！\n"
            "『それでは次のステージを開始します！』"
        )

        # --- 最終プロンプト（キャラ設定を追加） ---
        prompt = (
            "あなたはゲームの進行役で、プレイヤーを盛り上げる実況キャラです。\n"
            "語尾やテンションは自由ですが、楽しく・親しみやすく・少しお茶目に話してください。\n"
            "ただし、内容は事実に基づき、250字以内でまとめてください。\n\n"
            f"{comment}\n\n{question}\n\n{closing}"
        )

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"通信エラーのため、予備情報で進行します。\n(エラー内容: {e})"


# ============================
# 3. ポップアップクラス
# ============================
class GamePopup:
    def __init__(self, title, width=1200, height=800):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#f0f0f0")

        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.custom_font = font.Font(family="Meiryo", size=18, weight="bold")
        self.btn_font = font.Font(family="Meiryo", size=16, weight="bold")

    def show_simple(self, message):
        tk.Label(
            self.root, text=message, font=self.custom_font,
            wraplength=1000, bg="#f0f0f0", pady=100
        ).pack(expand=True)

        tk.Button(
            self.root, text="OK", font=self.btn_font,
            command=self.root.destroy, bg="#0078d7", fg="white",
            padx=60, pady=20
        ).pack(pady=50)

        self.root.mainloop()

    def show_ai_transition(self, score, ai_navigator):
        label_text = tk.StringVar()
        label_text.set(
            f"【 ステージ終了 】\n\n現在のスコア： {score} 点\n\nAIナビゲーターが最新情報取得中..."
        )

        label = tk.Label(
            self.root, textvariable=label_text, font=self.custom_font,
            wraplength=1000, justify="left", bg="#f0f0f0",
            padx=50, pady=50
        )
        label.pack(expand=True, fill="both")

        btn = tk.Button(
            self.root, text="準備中...", font=self.btn_font,
            state="disabled", command=self.root.destroy,
            bg="#cccccc", fg="white", padx=40, pady=20
        )
        btn.pack(pady=40)

        def fetch():
            ai_msg = ai_navigator.get_briefing(score)
            self.root.after(0, lambda: label_text.set(ai_msg))
            self.root.after(0, lambda: btn.config(
                state="normal", bg="#0078d7", text="ＯＫ！　次へ進む"
            ))

        threading.Thread(target=fetch, daemon=True).start()
        self.root.mainloop()


# ============================
# 4. ステージ設定
# ============================
STAGES = [
    {"id": 1, "file": "game001.py", "title": "STAGE 1",
     "msg": "【第１ステージ】\n\n新しい冒険の始まりだ！ゴールを目指して頑張ろう！"},
    {"id": 2, "file": "game002.py", "title": "STAGE 2",
     "msg": "【第２ステージ】\n\nインベーダー戦！タコお化けを倒せ！"},
    {"id": 3, "file": "game003.py", "title": "STAGE 3",
     "msg": "【第３ステージ】\n\n君こそパックマン！敵に捕まらないよう食べつくせ！"},
]


# ============================
# 5. ユーティリティ
# ============================
def run_script(script_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, script_name)
    if os.path.exists(script_path):
        subprocess.call([sys.executable, script_path])


# ============================
# 6. メイン処理
# ============================
def main():

    # --- APIキーを1回だけ読み込む ---
    if not os.path.exists("API_KEY.txt"):
        print("API_KEY.txt が見つかりません。")
        return

    with open("API_KEY.txt", "r", encoding="utf-8") as f:
        api_key = f.read().strip()

    # --- クラス初期化 ---
    score_manager = ScoreManager()
    ai_navigator = AINavigator(api_key)

    # --- ステージループ ---
    for i, stage in enumerate(STAGES):

        GamePopup(stage["title"]).show_simple(stage["msg"])

        run_script(stage["file"])

        if i < len(STAGES) - 1:
            GamePopup("AI実況ナビゲーター").show_ai_transition(
                score_manager.get(), ai_navigator
            )

    # --- 全クリア ---
    GamePopup("ALL CLEAR!").show_simple(
        f"お疲れ様！！\nゲーム終了です！\n\n最終スコア: {score_manager.get()} 点"
    )

    sys.exit()


if __name__ == "__main__":
    main()
