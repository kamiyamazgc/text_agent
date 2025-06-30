import os
import re
import logging
from datetime import datetime
from typing import List, Dict, Any
try:
    import openai
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    openai = None  # type: ignore
    OpenAI = None  # type: ignore

from ..utils.markdown_utils import (
    is_markdown_file,
    extract_critical_markdown_blocks,
    restore_critical_markdown_blocks
)

logger = logging.getLogger(__name__)


class DiffProcessor:
    """LLM-based text improvement using unified diff format."""
    
    def __init__(
        self,
        model: str = "gpt-4",
        max_chunk_size: int = 2000,
        max_retries: int = 3,
        output_history: bool = True,
        history_dir: str = "output_history",
        improvement_focus: str = "advanced_style",
        temp_dir: str = None
    ):
        """Initialize DiffProcessor with LLM-based text improvement."""
        if OpenAI is None:
            raise ImportError("openai is required for DiffProcessor")
            
        self.model = model
        self.max_chunk_size = max_chunk_size
        self.max_retries = max_retries
        self.output_history = output_history
        self.history_dir = history_dir
        self.improvement_focus = improvement_focus
        self.iteration_count = 0
        self.temp_dir = temp_dir  # New: temp directory for case-specific files
        
        if self.output_history:
            if self.temp_dir:
                # Use case-specific temp directory
                os.makedirs(self.temp_dir, exist_ok=True)
            else:
                # Fallback to global history directory
                os.makedirs(self.history_dir, exist_ok=True)
    
    def split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into manageable chunks while preserving context."""
        if len(text) <= self.max_chunk_size:
            return [text]
        
        # Markdownファイルの場合は特別な処理
        if is_markdown_file(text):
            return self._split_markdown_into_chunks(text)
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= self.max_chunk_size:
                current_chunk += paragraph + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + '\n\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_markdown_into_chunks(self, text: str) -> List[str]:
        """Split Markdown text into chunks while preserving block boundaries and headers."""
        # まずMarkdownブロックを抽出（重要な要素のみ）
        processed_text, markdown_blocks = extract_critical_markdown_blocks(text)
        
        # プレースホルダーの位置を記録
        placeholder_positions = []
        for placeholder, original in markdown_blocks.items():
            pos = processed_text.find(placeholder)
            if pos != -1:
                placeholder_positions.append((pos, placeholder, original))
        
        # 位置でソート
        placeholder_positions.sort(key=lambda x: x[0])
        
        # チャンク境界を決定（Markdownブロックを分割しないように）
        chunks = []
        current_chunk = ""
        current_pos = 0
        
        for pos, placeholder, original in placeholder_positions:
            # プレースホルダーまでのテキストを追加
            text_before = processed_text[current_pos:pos]
            
            # ヘッダープレースホルダーの場合は新しいチャンクを開始
            is_header = 'HEADER' in placeholder
            
            if is_header:
                # 現在のチャンクを保存
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                # 新しいチャンクを開始（ヘッダー用）
                current_chunk = text_before + placeholder
            else:
                # 通常の要素の場合
                if len(current_chunk) + len(text_before) + len(placeholder) <= self.max_chunk_size:
                    current_chunk += text_before + placeholder
                else:
                    # 現在のチャンクを保存
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    # 新しいチャンクを開始
                    current_chunk = text_before + placeholder
            
            current_pos = pos + len(placeholder)
        
        # 残りのテキストを追加
        remaining_text = processed_text[current_pos:]
        if len(current_chunk) + len(remaining_text) <= self.max_chunk_size:
            current_chunk += remaining_text
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = remaining_text
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # 空のチャンクを除去
        chunks = [chunk for chunk in chunks if chunk.strip()]
        
        return chunks
    
    def generate_diff_prompt(self, text: str) -> str:
        """Generate prompt for LLM to produce improved text directly."""
        focus_descriptions = {
            "advanced_style": "文章の流れと自然さの向上、専門用語の適切な使用、読み手への配慮（敬語、丁寧語の統一）、論理的な構成の改善、冗長な表現の簡潔化",
            "grammar_style": "文法の改善、表現の自然さ向上、読みやすさの改善、一貫性の確保",
            "business_style": "ビジネス文書としての適切性、敬語の統一、専門用語の適切な使用、論理的な構成"
        }
        
        focus_desc = focus_descriptions.get(self.improvement_focus, focus_descriptions["advanced_style"])
        
        # 重要なMarkdownプレースホルダーを検出（見出し・表・画像のみ）
        critical_placeholders = re.findall(r'__CRITICAL_[A-Z_]+_\d+__', text)
        image_placeholders = [p for p in critical_placeholders if 'IMAGE' in p]
        table_placeholders = [p for p in critical_placeholders if 'TABLE' in p]
        header_placeholders = [p for p in critical_placeholders if 'HEADER' in p]
        
        prompt = f"""以下のテキストを改善してください。

改善内容：{focus_desc}

【最重要】以下のプレースホルダーは絶対に変更・削除しないでください：

見出し: {chr(10).join(header_placeholders)}
表: {chr(10).join(table_placeholders)}
画像: {chr(10).join(image_placeholders)}

【Markdown形式の保持 - 絶対禁止事項】
- 見出しプレースホルダーの前後には必ず空行を入れてください
- 見出しは独立した行に配置してください
- 段落の前後にも適切な空行を保持してください

【Markdownリンク形式の保持 - 最重要】
- [text](url) 形式のMarkdownリンクは絶対に変更しないでください
- リンクテキスト [text] とURL (url) の構造を完全に保持してください
- バックスラッシュ（\\）はMarkdownのエスケープ文字として機能するため、絶対に変更・削除・追加しないでください
- 括弧（()）の前のバックスラッシュは、Markdownで括弧を文字として表示するために必要です

【バックスラッシュとエスケープ - 最重要】
- 既存のバックスラッシュ（\\）は絶対に変更・削除・追加しないでください
- 括弧（()）の前のバックスラッシュはそのまま保持してください
- 新しいバックスラッシュを追加しないでください
- エスケープ処理は一切行わないでください
- 元のテキストのバックスラッシュパターンを完全に保持してください

例：
- 入力: [\\(text\\)](url) → 出力: [\\(text\\)](url) （Markdownリンク形式を保持）
- 入力: [text](url) → 出力: [text](url) （Markdownリンク形式を保持）
- 入力: [\\(OpenAI,\\)](#page-21-0) → 出力: [\\(OpenAI,\\)](#page-21-0) （バックスラッシュを保持）

これらのプレースホルダーは文書の構造を表すため、そのまま保持してください。

改善されたテキストのみを返してください：

{text}"""
        
        return prompt
    
    def save_iteration(self, text: str, chunk_num: int) -> str:
        """Save iteration result to history file."""
        if not self.output_history:
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Use temp_dir if available, otherwise fallback to history_dir
        save_dir = self.temp_dir if self.temp_dir else self.history_dir
        
        # Save the improved text
        filename = f"output_fixed_{chunk_num}_{timestamp}.txt"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        logger.debug("Saved improved text for chunk %s to %s", chunk_num, filepath)
        return filepath
    
    def process(self, text: str) -> Dict[str, Any]:
        """Process text through LLM-based improvement with unified diff."""
        if not text.strip():
            return {"text": text, "metadata": {"iterations": 0, "changed": False}}
        
        logger.debug("DiffProcessor processing text of length %s", len(text))
        
        # Markdownファイルの場合は見出し・表・画像を絶対保護
        critical_blocks = {}
        if is_markdown_file(text):
            logger.debug("Markdown file detected")
            # 見出し・表・画像を絶対保護
            text, critical_blocks = extract_critical_markdown_blocks(text)
            logger.debug(
                "Protected %s critical blocks (headers, tables, images)",
                len(critical_blocks),
            )
        
        # 通常のDiffProcessor処理
        original_text = text
        improved_text = text
        iterations = 0
        changed = False
        
        # Split into chunks if needed
        chunks = self.split_text_into_chunks(text)
        logger.debug("Split into %s chunks", len(chunks))
        
        if len(chunks) > 1:
            # Process each chunk separately
            improved_chunks = []
            for i, chunk in enumerate(chunks):
                logger.debug("Processing chunk %s/%s", i + 1, len(chunks))
                improved_chunk = self._process_chunk(chunk, i+1)
                improved_chunks.append(improved_chunk)
            
            improved_text = '\n\n'.join(improved_chunks)
            iterations = 1
        else:
            # Process as single chunk
            improved_text = self._process_chunk(text, 1)
            iterations = 1
        
        # 見出し・表・画像を必ず復元
        if critical_blocks:
            logger.debug("Restoring critical markdown blocks (headers, tables, images)")
            improved_text = restore_critical_markdown_blocks(improved_text, critical_blocks)
            logger.debug("Restored %s critical blocks", len(critical_blocks))
        
        changed = improved_text != original_text
        
        return {
            "text": improved_text,
            "metadata": {
                "iterations": iterations,
                "changed": changed,
                "model": self.model,
                "improvement_focus": self.improvement_focus
            }
        }
    
    def _process_chunk(self, chunk: str, chunk_num: int) -> str:
        """Process a single chunk of text."""
        logger.debug("=== DiffProcessor: 入力チャンク（最初の100文字） ===")
        logger.debug(repr(chunk[:100]))
        
        original_chunk = chunk
        improved_chunk = chunk
        
        for attempt in range(self.max_retries):
            try:
                # Generate improvement prompt
                prompt = self.generate_diff_prompt(improved_chunk)
                
                logger.debug("=== DiffProcessor: LLM送信前テキスト（最初の100文字） ===")
                logger.debug(repr(improved_chunk[:100]))
                
                # Call LLM for direct text improvement
                client = OpenAI()
                resp = client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                )
                
                improved_response = resp.choices[0].message.content.strip()
                logger.debug("=== DiffProcessor: LLM返却テキスト（最初の100文字） ===")
                logger.debug(repr(improved_response[:100]))
                logger.debug(
                    "Received improvement response of length %s",
                    len(improved_response),
                )
                
                # Validate the response
                if improved_response and improved_response != original_chunk:
                    improved_chunk = improved_response
                    logger.debug("Chunk %s improved successfully", chunk_num)
                    break
                else:
                    logger.debug("No improvement in attempt %s", attempt + 1)
                    
            except Exception as e:
                logger.debug("Error in attempt %s: %s", attempt + 1, e)
                if attempt == self.max_retries - 1:
                    logger.debug("Max retries reached for chunk %s, keeping original", chunk_num)
        
        # Save iteration result
        if self.output_history:
            self.save_iteration(improved_chunk, chunk_num)
        
        return improved_chunk 