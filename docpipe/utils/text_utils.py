import re
from typing import List


def split_into_chunks(text: str, max_tokens: int = 2048) -> List[str]:
    """
    Split text into chunks based on token count estimation.
    Preserves Markdown headers and paragraph structure.
    
    Args:
        text: The text to split
        max_tokens: Maximum tokens per chunk
        
    Returns:
        List of text chunks
    """
    if not text.strip():
        return [""]
    
    # Simple token estimation: split by whitespace and count
    # This is a rough approximation for token counting
    words = text.split()
    
    if len(words) <= max_tokens:
        return [text]
    
    # Estimate tokens per character (rough approximation)
    total_chars = len(text)
    estimated_tokens_per_char = len(words) / total_chars if total_chars > 0 else 0.2
    
    # Calculate approximate characters per chunk
    chars_per_chunk = int(max_tokens / estimated_tokens_per_char)
    
    # Split text into lines to preserve structure
    lines = text.split('\n')
    chunks = []
    current_chunk = ""
    current_chars = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this line is a Markdown header
        is_header = bool(re.match(r'^#{1,6}\s+', line.strip()))
        
        # If it's a header, ensure it starts a new chunk
        if is_header:
            # Save current chunk if it exists
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = ""
                current_chars = 0
            
            # Add header with proper spacing
            if current_chunk:
                current_chunk += '\n\n' + line
            else:
                current_chunk = line
            current_chars += len(line) + 2  # +2 for the newlines
            
            # Move to next line
            i += 1
            continue
        
        # For non-header lines, check if adding this line would exceed the limit
        line_with_newline = line + '\n'
        
        if current_chars + len(line_with_newline) > chars_per_chunk and current_chunk:
            # Save current chunk and start new one
            chunks.append(current_chunk.strip())
            current_chunk = line_with_newline
            current_chars = len(line_with_newline)
        else:
            # Add to current chunk
            current_chunk += line_with_newline
            current_chars += len(line_with_newline)
        
        i += 1
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # If we still have chunks that are too long, split them further
    final_chunks = []
    for chunk in chunks:
        if len(chunk.split()) > max_tokens:
            # Split by paragraphs while preserving headers
            sub_chunks = split_chunk_by_paragraphs(chunk)
            for sub_chunk in sub_chunks:
                if sub_chunk.strip():
                    final_chunks.append(sub_chunk.strip())
        else:
            final_chunks.append(chunk)
    
    return final_chunks if final_chunks else [text]


def split_chunk_by_paragraphs(chunk: str) -> List[str]:
    """
    Split a chunk by paragraphs while preserving Markdown headers.
    """
    lines = chunk.split('\n')
    paragraphs = []
    current_paragraph = ""
    
    for line in lines:
        # Check if this line is a header
        is_header = bool(re.match(r'^#{1,6}\s+', line.strip()))
        
        if is_header:
            # Save current paragraph if it exists
            if current_paragraph.strip():
                paragraphs.append(current_paragraph.strip())
                current_paragraph = ""
            
            # Start new paragraph with header
            current_paragraph = line
        else:
            # Add line to current paragraph
            if current_paragraph:
                current_paragraph += '\n' + line
            else:
                current_paragraph = line
    
    # Add the last paragraph
    if current_paragraph.strip():
        paragraphs.append(current_paragraph.strip())
    
    return paragraphs 