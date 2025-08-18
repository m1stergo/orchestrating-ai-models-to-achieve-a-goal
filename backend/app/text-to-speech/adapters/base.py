"""
Base adapter interface for text-to-speech models.
"""
from abc import ABC, abstractmethod
from typing import Optional


class TextToSpeechAdapter(ABC):
    """Base interface for text-to-speech adapters."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the adapter is available."""
        pass

    @abstractmethod
    async def generate_speech(self, text: str, audio_prompt_url: Optional[str] = None) -> bytes:
        """
        Generate speech from text using the TTS model.
        
        Args:
            text: Text to convert to speech
            audio_prompt_url: Optional URL to audio prompt file for voice cloning
            
        Returns:
            bytes: Audio data as WAV bytes
        """
        pass
