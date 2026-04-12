import os
import docx
from google import genai

# 1. APIキーの設定
client = genai.Client(
    api_key="AIzaSyC1jeSbSXQJxUYL4bkjM9-zkSNI_sbopAw",
    http_options={'api_version': 'v1'}
)

def read_word(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

file_path = r"C:\Users\qayia\OneDrive\HP-PC\Doc001.docx"

try:
    content = read_word(file_path)
    print("AIが回答を生成中（最新モデル Gemini 2.5 Flash を使用）...")

    # 2. リストで確認できた「models/gemini-2.5-flash」を直接指定
    response = client.models.generate_content(
        model="models/gemini-2.5-flash", 
        contents=f"以下のドップラー効果に関する説明を読み、重要ポイントを3つ教えてください。\n\n内容：{content}"
    )

    print("\n--- ドップラー効果の重要ポイント ---")
    print(response.text)

except Exception as e:
    print(f"エラーが発生しました: {e}")