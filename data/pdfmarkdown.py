# pip install -U docling docling-core transformers pillow

from pathlib import Path
import re, json
from typing import List, Dict

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

# ---- 入力PDF（厚労省） ----
#DOC_SOURCE = "https://www.mhlw.go.jp/content/001018385.pdf"  # ユーザ指定URL
DOC_SOURCE="C:\\WorkSpace\\HandsOnTest\\001018385.pdf"
# ---- Doclingの変換設定（表をMarkdown化しやすく）----
pipeline_options = PdfPipelineOptions(
    do_table_structure=True,   # 表構造を復元（Markdownテーブル品質↑）
)
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE  # 精度重視
# 画像はピクセル出力しない（キャプションだけを後処理で残す）
pipeline_options.generate_page_images = False
pipeline_options.generate_picture_images = False

converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)

result = converter.convert(DOC_SOURCE)
dl_doc = result.document

# ---- Markdownを取得（画像参照は付けない）----
# Serializerを直呼びでもOK：dl_doc.export_to_markdown()
md_text = dl_doc.export_to_markdown()

# ---- 「画像キャプションだけ残す」後処理
# 例： ![図1　○○](path/to/img.png) → 図: 図1　○○
def strip_image_links_keep_captions(md: str) -> str:
    # ![caption](url) を "図: caption" に置換
    pattern = re.compile(r'!\[(?P<cap>[^\]]*)\]\([^)]+\)')
    return pattern.sub(lambda m: f"図: {m.group('cap')}".strip(), md)

md_caption_only = strip_image_links_keep_captions(md_text)

# ---- 保存（任意）：Markdown全文 & 章ごとのJSONL（ベクトル投入向け）
out_dir = Path("C:\WorkSpace\HandsOnTest\out_mhlw")
out_dir.mkdir(parents=True, exist_ok=True)

(out_dir / "mhlw_full_caption_only.md").write_text(md_caption_only, encoding="utf-8")

print(f"Markdown（キャプションのみ）: {out_dir/'mhlw_full_caption_only.md'}")
