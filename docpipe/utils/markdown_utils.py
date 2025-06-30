import re
from typing import List, Tuple, Dict, Any


def is_markdown_file(text: str) -> bool:
    """Check if the text contains Markdown formatting."""
    markdown_patterns = [
        r'^#{1,6}\s+',  # Headers
        r'\*\*.*?\*\*',  # Bold
        r'\*.*?\*',      # Italic
        r'`.*?`',        # Inline code
        r'```[\s\S]*?```',  # Code blocks
        r'!\[.*?\]\(.*?\)',  # Images
        r'\[.*?\]\(.*?\)',   # Links
        r'^\s*[-*+]\s+',     # Unordered lists
        r'^\s*\d+\.\s+',     # Ordered lists
        r'^\s*>\s+',         # Blockquotes
        r'^\|.*\|$',         # Tables
        r'^\s*---+\s*$',     # Horizontal rules
    ]
    
    for pattern in markdown_patterns:
        if re.search(pattern, text, re.MULTILINE):
            return True
    return False


def extract_critical_markdown_blocks(text: str) -> Tuple[str, Dict[str, str]]:
    """
    Extract only table, image, and header blocks as critical Markdown, in that order.
    Do NOT protect bold, link, or other markdown elements.
    """
    blocks = {}
    block_counter = 0

    # 1. 表を最優先で検出・保護
    def find_and_replace_tables(text):
        nonlocal block_counter
        lines = text.split('\n')
        result_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # | で始まり | で終わる行が連続している部分を表とみなす
            if line.strip().startswith('|') and line.strip().endswith('|'):
                table_lines = [line]
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    if next_line.strip().startswith('|') and next_line.strip().endswith('|'):
                        table_lines.append(next_line)
                        i += 1
                    else:
                        break
                table_block = '\n'.join(table_lines)
                placeholder = f"__CRITICAL_TABLE_{block_counter}__"
                blocks[placeholder] = table_block
                block_counter += 1
                result_lines.append(placeholder)
            else:
                result_lines.append(line)
                i += 1
        return '\n'.join(result_lines)
    text = find_and_replace_tables(text)

    # 2. 画像 (![...](...))
    def replace_image(match):
        nonlocal block_counter
        placeholder = f"__CRITICAL_IMAGE_{block_counter}__"
        blocks[placeholder] = match.group(0)
        block_counter += 1
        return placeholder
    text = re.sub(r'!\[.*?\]\([^)]+\)', replace_image, text, flags=re.MULTILINE | re.DOTALL)

    # 3. 見出し (# ...) - 行の先頭にある見出しのみを検出（前後の改行も含める）
    def replace_header(match):
        nonlocal block_counter
        # 見出しの前後の改行も含めて保存
        line_start = match.start()
        line_end = match.end()
        
        # 前の改行を検出
        prev_newline = ""
        if line_start > 0 and text[line_start-1] == '\n':
            prev_newline = "\n"
        
        # 後の改行を検出
        next_newline = ""
        if line_end < len(text) and text[line_end] == '\n':
            next_newline = "\n"
        
        placeholder = f"__CRITICAL_HEADER_{block_counter}__"
        # 前後の改行も含めて保存
        blocks[placeholder] = prev_newline + match.group(0) + next_newline
        block_counter += 1
        return placeholder
    
    # 行の先頭にある見出しのみを検出（行の途中の見出し記号は無視）
    text = re.sub(r'^#{1,6}\s+.*$', replace_header, text, flags=re.MULTILINE)

    return text, blocks


def restore_critical_markdown_blocks(text: str, blocks: Dict[str, str]) -> str:
    """Restore critical Markdown formatting blocks from placeholders."""
    for placeholder, original in blocks.items():
        # 見出しの場合は前後の改行が既に含まれているのでそのまま復元
        text = text.replace(placeholder, original)
    return text


def extract_markdown_blocks(text: str) -> Tuple[str, Dict[str, str]]:
    """
    Extract Markdown formatting blocks and replace them with placeholders.
    Returns the processed text and a mapping of placeholders to original blocks.
    """
    blocks = {}
    block_counter = 0
    
    # Images (![...](...)) - より強力な保護
    def replace_image(match):
        nonlocal block_counter
        placeholder = f"__MARKDOWN_IMAGE_{block_counter}__"
        blocks[placeholder] = match.group(0)
        block_counter += 1
        return placeholder
    
    # 画像パターンを複数行対応で検出
    text = re.sub(r'!\[.*?\]\([^)]+\)', replace_image, text, flags=re.MULTILINE | re.DOTALL)
    
    # Code blocks (```...```)
    def replace_code_block(match):
        nonlocal block_counter
        placeholder = f"__MARKDOWN_CODE_BLOCK_{block_counter}__"
        blocks[placeholder] = match.group(0)
        block_counter += 1
        return placeholder
    
    text = re.sub(r'```[\s\S]*?```', replace_code_block, text)
    
    # Tables (|...| lines) - 複数行の表を一つのブロックとして保護
    def replace_table(match):
        nonlocal block_counter
        placeholder = f"__MARKDOWN_TABLE_{block_counter}__"
        blocks[placeholder] = match.group(0)
        block_counter += 1
        return placeholder
    
    # 表の開始から終了までを一つのブロックとして検出
    text = re.sub(r'(^\|.*\|$)(?:\n^\|.*\|$)*', replace_table, text, flags=re.MULTILINE)
    
    # Headers (# ## ### etc.) - 見出し記号と内容を分離して保護
    def replace_header(match):
        nonlocal block_counter
        placeholder = f"__MARKDOWN_HEADER_{block_counter}__"
        blocks[placeholder] = match.group(0)
        block_counter += 1
        return placeholder
    
    text = re.sub(r'^#{1,6}\s+.*$', replace_header, text, flags=re.MULTILINE)
    
    # Links ([...](...))
    def replace_link(match):
        nonlocal block_counter
        placeholder = f"__MARKDOWN_LINK_{block_counter}__"
        blocks[placeholder] = match.group(0)
        block_counter += 1
        return placeholder
    
    text = re.sub(r'\[.*?\]\(.*?\)', replace_link, text)
    
    # Bold (**text**)
    def replace_bold(match):
        nonlocal block_counter
        placeholder = f"__MARKDOWN_BOLD_{block_counter}__"
        blocks[placeholder] = match.group(0)
        block_counter += 1
        return placeholder
    
    text = re.sub(r'\*\*.*?\*\*', replace_bold, text)
    
    # Italic (*text*)
    def replace_italic(match):
        nonlocal block_counter
        placeholder = f"__MARKDOWN_ITALIC_{block_counter}__"
        blocks[placeholder] = match.group(0)
        block_counter += 1
        return placeholder
    
    text = re.sub(r'\*.*?\*', replace_italic, text)
    
    # Inline code (`code`)
    def replace_inline_code(match):
        nonlocal block_counter
        placeholder = f"__MARKDOWN_INLINE_CODE_{block_counter}__"
        blocks[placeholder] = match.group(0)
        block_counter += 1
        return placeholder
    
    text = re.sub(r'`.*?`', replace_inline_code, text)
    
    # Lists (- * +)
    def replace_list_item(match):
        nonlocal block_counter
        placeholder = f"__MARKDOWN_LIST_ITEM_{block_counter}__"
        blocks[placeholder] = match.group(0)
        block_counter += 1
        return placeholder
    
    text = re.sub(r'^\s*[-*+]\s+.*$', replace_list_item, text, flags=re.MULTILINE)
    
    # Ordered lists (1. 2. etc.)
    def replace_ordered_list(match):
        nonlocal block_counter
        placeholder = f"__MARKDOWN_ORDERED_LIST_{block_counter}__"
        blocks[placeholder] = match.group(0)
        block_counter += 1
        return placeholder
    
    text = re.sub(r'^\s*\d+\.\s+.*$', replace_ordered_list, text, flags=re.MULTILINE)
    
    # Blockquotes (> text)
    def replace_blockquote(match):
        nonlocal block_counter
        placeholder = f"__MARKDOWN_BLOCKQUOTE_{block_counter}__"
        blocks[placeholder] = match.group(0)
        block_counter += 1
        return placeholder
    
    text = re.sub(r'^\s*>\s+.*$', replace_blockquote, text, flags=re.MULTILINE)
    
    return text, blocks


def restore_markdown_blocks(text: str, blocks: Dict[str, str]) -> str:
    """Restore Markdown formatting blocks from placeholders."""
    for placeholder, original in blocks.items():
        text = text.replace(placeholder, original)
    return text


def get_text_for_evaluation(text: str) -> str:
    """
    Extract text content suitable for evaluation, excluding Markdown formatting.
    """
    if not is_markdown_file(text):
        return text
    
    # Extract and remove critical Markdown blocks only
    processed_text, blocks = extract_critical_markdown_blocks(text)
    
    # Remove remaining Markdown syntax that might interfere with evaluation
    # Remove horizontal rules
    processed_text = re.sub(r'^\s*[-*_]{3,}\s*$', '', processed_text, flags=re.MULTILINE)
    
    # Remove table separators
    processed_text = re.sub(r'^\s*\|[-:\s|]+\|\s*$', '', processed_text, flags=re.MULTILINE)
    
    # Clean up extra whitespace
    processed_text = re.sub(r'\n\s*\n\s*\n', '\n\n', processed_text)
    processed_text = processed_text.strip()
    
    return processed_text 