import requests
import json
from tqdm import tqdm
import os


def getEmbed(input):
    # APIキーの設定
    api_key = os.getenv('OPENAI_API_KEY')

    # リクエストURL
    url = "https://api.openai.com/v1/embeddings"
    # ヘッダー
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # リクエストボディ
    data = {
        "model": "text-embedding-3-small",  # または "text-embedding-3-large", "text-embedding-ada-002"
        "input": input, 
        "encoding_format": "float"
    }

    # HTTPリクエスト送信
    response = requests.post(url, headers=headers, json=data)
    embeddingstr=None
    # レスポンス確認
    if response.status_code == 200:
        result = response.json()
        embedding = result['data'][0]['embedding']
        #print(f"成功: ベクトル次元数 = {len(embedding)}")
        embeddingstr=str(embedding)[1:-1]
    else:
        print(f"エラー: {response.status_code}")
        print(response.text)
    
    return embeddingstr



def addVector(infile,outfile):
    with open(infile, "r", encoding="utf-8") as f:
        originaldocs = [json.loads(line) for line in f]

    #print(originaldocs[:2])

    openai_text_embeddings = []

    for doc in tqdm(originaldocs, desc="Encoding text with OpenAI"):
        openai_text_embeddings.append(getEmbed(doc["text"]))

    openai_text_vectors = [
        {"source": doc["source"], "title":doc["title"],"text":doc["text"],"textvec": embedding}
        for doc, embedding in zip(originaldocs, openai_text_embeddings)
    ]

    with open(outfile, "w", encoding="utf-8") as f:
        for item in openai_text_vectors:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
