import pytest
from unittest.mock import Mock, patch
from docpipe.processors.diff_processor import DiffProcessor


class TestDiffProcessor:
    """Test DiffProcessor functionality."""
    
    def test_init(self):
        """Test DiffProcessor initialization."""
        processor = DiffProcessor(
            model="gpt-4",
            max_chunk_size=2000,
            max_retries=3,
            output_history=True,
            history_dir="test_history",
            improvement_focus="advanced_style"
        )
        
        assert processor.model == "gpt-4"
        assert processor.max_chunk_size == 2000
        assert processor.max_retries == 3
        assert processor.output_history is True
        assert processor.history_dir == "test_history"
        assert processor.improvement_focus == "advanced_style"
        assert processor.iteration_count == 0
    
    def test_split_text_into_chunks_small_text(self):
        """Test text splitting with small text."""
        processor = DiffProcessor()
        text = "This is a short text."
        chunks = processor.split_text_into_chunks(text)
        
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_split_text_into_chunks_large_text(self):
        """Test text splitting with large text."""
        processor = DiffProcessor(max_chunk_size=50)
        text = "This is paragraph one.\n\nThis is paragraph two.\n\nThis is paragraph three."
        chunks = processor.split_text_into_chunks(text)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 50 for chunk in chunks)
    
    def test_generate_diff_prompt(self):
        """Test diff prompt generation."""
        processor = DiffProcessor(improvement_focus="advanced_style")
        text = "テストテキストです。"
        prompt = processor.generate_diff_prompt(text)
        
        assert "Unified Diff形式" in prompt
        assert text in prompt
        assert "advanced_style" in prompt or "文章の流れ" in prompt
    
    def test_generate_diff_prompt_business_style(self):
        """Test diff prompt generation with business style."""
        processor = DiffProcessor(improvement_focus="business_style")
        text = "テストテキストです。"
        prompt = processor.generate_diff_prompt(text)
        
        assert "ビジネス文書" in prompt
    
    @patch('docpipe.processors.diff_processor.fromstring')
    @patch('docpipe.processors.diff_processor.apply_patch')
    def test_apply_unified_diff_success(self, mock_apply_patch, mock_fromstring):
        """Test successful diff application."""
        processor = DiffProcessor()
        original_text = "Original text"
        diff_text = "--- a\n+++ b\n@@ -1,1 +1,1 @@\n-Original text\n+Improved text"
        
        mock_patch = Mock()
        mock_fromstring.return_value = mock_patch
        mock_apply_patch.return_value = "Improved text"
        
        result = processor.apply_unified_diff(original_text, diff_text)
        
        assert result == "Improved text"
        mock_fromstring.assert_called_once_with(diff_text)
        mock_apply_patch.assert_called_once_with(original_text, mock_patch)
    
    def test_apply_unified_diff_failure(self):
        """Test diff application failure."""
        processor = DiffProcessor()
        original_text = "Original text"
        diff_text = "Invalid diff format"
        
        result = processor.apply_unified_diff(original_text, diff_text)
        
        assert result == original_text
    
    @patch('builtins.open', create=True)
    @patch('os.makedirs')
    def test_save_iteration(self, mock_makedirs, mock_open):
        """Test iteration saving."""
        processor = DiffProcessor(output_history=True, history_dir="test_dir")
        text = "Test text"
        iteration = 1
        
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = processor.save_iteration(text, iteration)
        
        assert "output_fixed_1_" in result
        assert result.endswith(".txt")
        mock_makedirs.assert_called_once_with("test_dir", exist_ok=True)
        mock_file.write.assert_called_once_with(text)
    
    def test_save_iteration_disabled(self):
        """Test iteration saving when disabled."""
        processor = DiffProcessor(output_history=False)
        text = "Test text"
        iteration = 1
        
        result = processor.save_iteration(text, iteration)
        
        assert result == ""
    
    @patch('openai.OpenAI')
    def test_process_with_changes(self, mock_openai):
        """Test processing with successful changes."""
        processor = DiffProcessor()
        text = "テストテキストです。"
        
        # Mock OpenAI response
        mock_client = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = """--- a
+++ b
@@ -1,1 +1,1 @@
-テストテキストです。
+改善されたテストテキストです。"""
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Mock patch application
        with patch.object(processor, 'apply_unified_diff', return_value="改善されたテストテキストです。") as mock_apply:
            result = processor.process(text)
            # Verify that apply_unified_diff was called
            mock_apply.assert_called()
        
        assert result["text"] == "改善されたテストテキストです。"
        assert result["changed"] is True
        assert result["iterations"] == 1
    
    @patch('openai.OpenAI')
    def test_process_no_changes(self, mock_openai):
        """Test processing with no changes."""
        processor = DiffProcessor()
        text = "テストテキストです。"
        
        # Mock OpenAI response with no diff
        mock_client = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "No changes needed"
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        result = processor.process(text)
        
        assert result["text"] == text
        assert result["changed"] is False
        assert result["iterations"] == 0
    
    def test_process_markdown_preservation(self):
        """Test that Markdown formatting is preserved."""
        processor = DiffProcessor()
        text = """# タイトル

これは**太字**のテキストです。

- リスト項目1
- リスト項目2

```python
print("コードブロック")
```"""
        
        with patch('openai.OpenAI'):
            result = processor.process(text)
        
        # Should preserve Markdown structure
        assert "# タイトル" in result["text"]
        assert "**太字**" in result["text"]
        assert "- リスト項目" in result["text"]
        assert "```python" in result["text"] 