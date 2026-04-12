import os
import sys
import docx
from google import genai

# --- 設定（変更しやすいように一箇所にまとめる） ---
API_KEY = "AIzaSyC1jeSbSXQJxUYL4bkjM9-zkSNI_sbopAw" 
MODEL_ID = "gemini-2.5-flash"  # モデル名を定数化
FILE_PATH = r"C:\Users\qayia\OneDrive\HP-PC\Doc001.docx"

def get_client(api_key):
    """AIクライアントを初期化する"""
    return genai.Client(
        api_key=api_key,
        http_options={'api_version': 'v1'}
    )

def read_word_text(path):
    """Wordファイルからテキストを抽出する"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"ファイルが見つかりません: {path}")
    
    doc = docx.Document(path)
    # 空行を除去して読みやすく連結
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)

def main():
    try:
        # 1. 準備
        client = get_client(API_KEY)
        content = read_word_text(FILE_PATH)
        
        if not content:
            print("Wordファイルの中身が空です。")
            return

        print(f"AIが回答を生成中（使用モデル: {MODEL_ID}）...")

        # 2. AIへリクエスト
        prompt = f"以下のドップラー効果に関する説明を読み、重要ポイントを3つ教えてください。\n\n内容：\n{content}"
        
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )

        # 3. 結果出力
        print("\n" + "="*30)
        print("--- ドップラー効果の重要ポイント ---")
        print("="*30)
        print(response.text)

    except Exception as e:
        print(f"\n【エラーが発生しました】\n{e}", file=sys.stderr)

if __name__ == "__main__":
    main()



