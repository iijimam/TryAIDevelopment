import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple

import tiktoken
from openai import OpenAI

# ======= 設定 =======
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # 事前に環境変数
MODEL_EMB = "text-embedding-3-small"

# チャンク関連（用途に合わせて調整）
MAX_TOKENS_PER_CHUNK = 800       # RAG向け：300〜800が目安
OVERLAP_TOKENS = 60              # 0〜100程度
BATCH_SIZE = 128                 # Embedding一括投入

# ======= Tokenizer（OpenAI系：cl100k_base） =======
enc = tiktoken.get_encoding("cl100k_base")

def tok_count(text: str) -> int:
    return len(enc.encode(text))

def tok_encode(text: str) -> List[int]:
    return enc.encode(text)

def tok_decode(tokens: List[int]) -> str:
    return enc.decode(tokens)

# ======= Markdown -> セクションごとの本文抽出（見出しをタイトルに） =======
RE_HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.*)$")

def parse_markdown_sections(markdown_path: str) -> List[Dict[str, str]]:
    """
    見出し階層をたどって title_path を作り、本文をセクション単位で収集。
    return: [{"title": "第1章 > 総則", "text": "...本文..."}, ...]
    """
    lines = Path(markdown_path).read_text(encoding="utf-8", errors="ignore").splitlines()
    levels = [""] * 6  # h1..h6 の現在値
    sections: List[Dict[str, str]] = []
    buf: List[str] = []

    def flush_buf():
        nonlocal buf
        text = "\n".join(buf).strip()
        if text:
            title_path = " > ".join([t for t in levels if t])
            if not title_path:
                title_path = "(無題)"
            sections.append({"title": title_path, "text": text})
        buf = []

    for ln in lines:
        m = RE_HEADING.match(ln)
        if m:
            # 新しい見出しが来たら、直前の本文をフラッシュ
            flush_buf()
            level = len(m.group(1))
            title = m.group(2).strip()
            # タイトル階層を更新
            levels[level-1] = title
            for i in range(level, 6):
                levels[i] = ""
        else:
            buf.append(ln)

    flush_buf()
    # 空行過多の正規化
    for s in sections:
        s["text"] = re.sub(r"\n{3,}", "\n\n", s["text"]).strip()
    # 見出しだけで本文が空のセクションは除外
    sections = [s for s in sections if s["text"]]
    return sections

# ======= 文・段落分割（日本語フレンドリー） =======
RE_SENT_BOUNDARY = re.compile(r"(?<=[。．！？!\?])\s+")
RE_EMPTY_PARA_SPLIT = re.compile(r"\n\s*\n")

def split_into_paragraphs(text: str) -> List[str]:
    return [p.strip() for p in RE_EMPTY_PARA_SPLIT.split(text) if p.strip()]

def split_paragraph_into_sentences(paragraph: str) -> List[str]:
    norm = re.sub(r"\s*\n\s*", " ", paragraph).strip()
    # 句点などで分割（スペース/改行で切る）
    sents = [s.strip() for s in RE_SENT_BOUNDARY.split(norm) if s.strip()]
    return sents if sents else ([norm] if norm else [])

def text_to_sentences(text: str) -> List[str]:
    sents: List[str] = []
    for para in split_into_paragraphs(text):
        sents.extend(split_paragraph_into_sentences(para))
    return sents

# 長文1文のセーフ分割（句読点や括弧で優先的にスライス）
CLAUSE_SEPS = r"[、，・；;：:／/（）\(\)［\[\]｛\{\}「」『』‥…]"

def split_long_sentence_by_clauses(sent: str, max_tokens: int) -> List[str]:
    toks = tok_encode(sent)
    if len(toks) <= max_tokens:
        return [sent]

    # 句読点・括弧などで候補を作る
    parts = re.split(f"({CLAUSE_SEPS})", sent)
    # parts = [chunk, sep, chunk, sep, ...]
    # sepも含めて再結合しつつ max_tokens 以下で詰める
    chunks: List[str] = []
    cur = ""
    for i in range(0, len(parts), 2):
        chunk = parts[i]
        sep = parts[i+1] if i+1 < len(parts) else ""
        piece = (chunk + sep).strip()
        if not piece:
            continue
        # 追加した場合のトークン数
        if tok_count(cur + piece) <= max_tokens:
            cur += piece
        else:
            if cur:
                chunks.append(cur.strip())
                cur = ""
            # piece単体が大きすぎるなら、最終手段：トークン安全分割
            if tok_count(piece) > max_tokens:
                toks_piece = tok_encode(piece)
                for j in range(0, len(toks_piece), max_tokens):
                    chunks.append(tok_decode(toks_piece[j:j+max_tokens]).strip())
            else:
                cur = piece
    if cur:
        chunks.append(cur.strip())
    return chunks

# ======= チャンク化（文単位パッキング＋オーバーラップ） =======
def pack_chunks_by_tokens_with_titles(
    sections: List[Dict[str, str]],
    max_tokens: int = MAX_TOKENS_PER_CHUNK,
    overlap_tokens: int = OVERLAP_TOKENS
) -> List[Dict[str, str]]:
    """
    入力: [{"title": "...", "text": "..."}]
    出力: [{"title": "...", "text": "..."}]  # チャンク列
    """
    chunks: List[Dict[str, str]] = []

    for sec in sections:
        title = sec["title"]
        sents = text_to_sentences(sec["text"])

        cur_tokens: List[int] = []
        cur_title = title

        def flush():
            nonlocal cur_tokens
            if cur_tokens:
                chunks.append({"title": cur_title, "text": tok_decode(cur_tokens)})
                cur_tokens = []

        for sent in sents:
            stoks = tok_encode(sent)

            # 1文がデカすぎる場合は、句読点等で安全分割
            if len(stoks) > max_tokens:
                for sub in split_long_sentence_by_clauses(sent, max_tokens):
                    subtoks = tok_encode(sub)
                    # 現バッファに入るかチェック
                    if len(cur_tokens) + len(subtoks) <= max_tokens:
                        cur_tokens.extend(subtoks)
                    else:
                        flush()
                        # オーバーラップ
                        if overlap_tokens > 0 and chunks:
                            prev = tok_encode(chunks[-1]["text"])
                            tail = prev[-overlap_tokens:] if len(prev) > overlap_tokens else prev
                            cur_tokens = tail[:]
                        else:
                            cur_tokens = []
                        # それでも溢れることはない（subはmax以内）
                        cur_tokens.extend(subtoks)
                continue

            # ここからは通常文
            if len(cur_tokens) + len(stoks) <= max_tokens:
                cur_tokens.extend(stoks)
                #以下、文単位で区切る場合。これだど短すぎる
                #flush()
                #cur_tokens = stoks[:]  # 文単位で切る
            else:
                flush()
                # オーバーラップ
                if overlap_tokens > 0 and chunks:
                    prev = tok_encode(chunks[-1]["text"])
                    tail = prev[-overlap_tokens:] if len(prev) > overlap_tokens else prev
                    cur_tokens = tail[:]
                else:
                    cur_tokens = []
                cur_tokens.extend(stoks)

        flush()

    return chunks

# ======= Embedding =======
def embed_texts(texts: List[str], model: str = MODEL_EMB, batch_size: int = BATCH_SIZE) -> List[List[float]]:
    client = OpenAI(api_key=OPENAI_API_KEY)
    vectors: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        if len(texts[i]) > batch_size :
            print(f"{len(texts[i])} - {texts[i]}")

        resp = client.embeddings.create(model=model, input=batch)
        vectors.extend([d.embedding for d in resp.data])
    return vectors

# ======= 全体パイプライン =======
def markdown_to_chunked_embeddings_with_titles(md_path: str, out_jsonl: str):
    sections = parse_markdown_sections(md_path)
    if not sections:
        raise ValueError("本文が空です。Markdownのパスや見出し構造を確認してください。")

    # 文尊重のチャンク化（セクション境界はまたがない）
    chunks = pack_chunks_by_tokens_with_titles(
        sections,
        max_tokens=MAX_TOKENS_PER_CHUNK,
        overlap_tokens=OVERLAP_TOKENS
    )

    # 埋め込み
    embs = embed_texts([c["text"] for c in chunks], model=MODEL_EMB, batch_size=BATCH_SIZE)

    # JSONL で保存（title 付き）
    with open(out_jsonl, "w", encoding="utf-8") as f:
        for idx, (c, vec) in enumerate(zip(chunks, embs), start=1):
            rec = {
                "id": f"mhlw-hr-{idx:05d}",
                "title": c["title"],            # ここに見出しパス
                "text": c["text"],
                "n_tokens": tok_count(c["text"]),
                "embedding": vec
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"✅ Done: {len(chunks)} chunks → {out_jsonl}")

# ======= 実行例 =======
if __name__ == "__main__":
    # Doclingで作ったMarkdown（厚労省モデル人事規程）
    markdown_to_chunked_embeddings_with_titles(
        md_path="C:\\WorkSpace\\HandsOnTest\\out_mhlw\\mhlw_full_caption_only.md",
        out_jsonl="C:\\WorkSpace\\HandsOnTest\\out_mhlw\\mhlw_hr_rules_chunk_embeddings.jsonl"
    )
