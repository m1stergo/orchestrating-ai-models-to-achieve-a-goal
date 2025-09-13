"""
Base adapter interface for text_to_speech models.
"""
from abc import ABC, abstractmethod
from typing import Optional
from app.shared.api_adapter import ApiAdapter


class TextToSpeechAdapter(ApiAdapter, ABC):
    @abstractmethod
    async def inference(self, text: str, voice_url: Optional[str] = None) -> bytes:
        """Run inference with the model to generate speech from text."""
        raise NotImplementedError
