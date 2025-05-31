from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseExtractor(ABC):
    """Base class for all document extractors"""
    
    @abstractmethod
    def extract(self, source: str, **kwargs) -> Dict[str, Any]:
        """
        Extract content from the source
        
        Args:
            source: Path or URL to the source document
            **kwargs: Additional extractor-specific parameters
            
        Returns:
            Dict containing:
            - text: str - The extracted text
            - metadata: Dict[str, Any] - Source-specific metadata
        """
        pass
    
    @abstractmethod
    def can_handle(self, source: str) -> bool:
        """
        Check if this extractor can handle the given source
        
        Args:
            source: Path or URL to check
            
        Returns:
            bool indicating if this extractor can handle the source
        """
        pass 
