import sys
import pathlib

def count_words(file_path):
    text = pathlib.Path(file_path).read_text(encoding='utf-8')
    # Split on whitespace and filter out empty strings
    words = [word for word in text.split() if word.strip()]
    return len(words)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python count_words.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    word_count = count_words(file_path)
    print(f"Number of words: {word_count}") 