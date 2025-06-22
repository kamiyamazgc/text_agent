import re
from pathlib import Path
from typing import Dict, Any, Optional
try:
    import yt_dlp  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yt_dlp = None  # type: ignore
from .base import BaseExtractor
from .audio import AudioExtractor

# 日本語文字パターン
JAPANESE_PATTERN = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
# 中国語文字パターン（簡体字・繁体字）
CHINESE_PATTERN = re.compile(r"[\u4e00-\u9fff]")
# 韓国語文字パターン
KOREAN_PATTERN = re.compile(r"[\uac00-\ud7af]")

def _detect_language(text: str) -> str:
    """Detect language based on character patterns."""
    if JAPANESE_PATTERN.search(text):
        return "ja"
    elif CHINESE_PATTERN.search(text):
        return "zh"
    elif KOREAN_PATTERN.search(text):
        return "ko"
    else:
        return "en"

class YouTubeExtractor(BaseExtractor):
    """Extractor for YouTube videos using captions or audio transcription"""
    
    def __init__(self, temp_dir: Path):
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def can_handle(self, source: str) -> bool:
        """Check if the source is a YouTube URL"""
        patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'https?://youtu\.be/[\w-]+',
            r'https?://(?:www\.)?youtube\.com/live/[\w-]+'
        ]
        return any(re.match(pattern, source) for pattern in patterns)
    
    def _get_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        if "youtu.be" in url:
            return url.split("/")[-1]
        elif "/live/" in url:
            # ライブ配信URLの場合
            match = re.search(r"/live/([\w-]+)", url)
            if not match:
                raise ValueError(f"Invalid YouTube live URL: {url}")
            return match.group(1)
        else:
            # 通常のwatch URLの場合
            match = re.search(r"v=([\w-]+)", url)
            if not match:
                raise ValueError(f"Invalid YouTube URL: {url}")
            return match.group(1)
    
    def _download_captions(self, video_id: str) -> Optional[str]:
        """Download auto-generated captions with priority for English"""
        if yt_dlp is None:
            raise ImportError("yt_dlp is required for YouTube extraction")
        try:
            with yt_dlp.YoutubeDL({'skip_download': True}) as ydl:
                info = ydl.extract_info(
                    f'https://www.youtube.com/watch?v={video_id}', download=False
                )
        except Exception as e:  # pragma: no cover - passthrough errors
            print(f"Failed to fetch video info: {e}")
            return None

        auto_caps = info.get('automatic_captions') or {}
        if not auto_caps:
            return None

        # 動画の言語を検出（タイトルと説明から）
        video_title = info.get('title', '')
        video_description = info.get('description', '')
        video_text = f"{video_title} {video_description}"
        video_language = _detect_language(video_text)

        # 動画が日本語の場合は日本語字幕を優先
        if video_language == 'ja':
            preferred_languages = ['ja', 'en', 'zh', 'ko']
        else:
            # その他の言語の場合は英語を優先
            preferred_languages = ['en', 'ja', 'zh', 'ko']
        
        selected_lang = None
        
        # 優先言語から順番に確認
        for lang in preferred_languages:
            if lang in auto_caps:
                selected_lang = lang
                break
        
        # 優先言語が見つからない場合は最初の利用可能な言語を使用
        if selected_lang is None:
            selected_lang = next(iter(auto_caps))

        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [selected_lang],
            'skip_download': True,
            'outtmpl': str(self.temp_dir / f'{video_id}.%(ext)s')
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
                caption_file = self.temp_dir / f'{video_id}.{selected_lang}.vtt'
                if caption_file.exists():
                    return caption_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Failed to download captions: {e}")
        return None
    
    def _download_audio(self, video_id: str) -> Optional[Path]:
        """Download audio for transcription"""
        if yt_dlp is None:
            raise ImportError("yt_dlp is required for YouTube extraction")
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'outtmpl': str(self.temp_dir / f'{video_id}.%(ext)s')
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f'https://www.youtube.com/watch?v={video_id}'])
                return self.temp_dir / f'{video_id}.mp3'
        except Exception as e:
            print(f"Failed to download audio: {e}")
        return None
    
    def extract(self, source: str, **kwargs) -> Dict[str, Any]:
        """Extract content from YouTube video"""
        video_id = self._get_video_id(source)
        metadata = {
            'source_type': 'youtube',
            'video_id': video_id,
            'caption_used': False
        }
        
        # Try to get captions first
        text = self._download_captions(video_id)
        if text:
            metadata['caption_used'] = True
            language = _detect_language(text)
            metadata['language'] = language
            metadata['needs_translation'] = language != 'ja'
            return {
                'text': text,
                'metadata': metadata
            }
        
        # Fallback to audio transcription
        audio_file = self._download_audio(video_id)
        if audio_file:
            try:
                audio_result = AudioExtractor().extract(str(audio_file))
            except Exception as e:  # pragma: no cover - passthrough any errors
                raise RuntimeError(f"Failed to transcribe audio: {e}") from e

            metadata['audio_file'] = audio_result['metadata'].get('file_name')
            metadata['audio_model'] = audio_result['metadata'].get('model')
            language = _detect_language(audio_result['text'])
            metadata['language'] = language
            metadata['needs_translation'] = language != 'ja'
            return {
                'text': audio_result['text'],
                'metadata': metadata
            }
        
        raise Exception("Failed to extract content from YouTube video")
