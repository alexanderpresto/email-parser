# email_parser/processor.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ProcessingConfig:
    output_directory: str
    convert_excel: bool = False
    max_attachment_size: int = 10_000_000
    batch_size: int = 100


@dataclass
class ProcessingResult:
    attachments: List[str] = field(default_factory=list)
    text_content: Optional[str] = None
    html_content: Optional[str] = None
    csv_files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EmailParser:
    def __init__(self, config: ProcessingConfig):
        self.config = config
        
    def process_email(self, email_path: str) -> ProcessingResult:
        # Placeholder - implement the actual email processing logic
        print(f"Processing email: {email_path}")
        return ProcessingResult(
            attachments=["sample_attachment.pdf"]
        )
        
    def process_batch(self, email_paths: List[str]) -> List[ProcessingResult]:
        results = []
        for path in email_paths:
            results.append(self.process_email(path))
        return results