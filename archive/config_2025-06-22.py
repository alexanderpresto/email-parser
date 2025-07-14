from dataclasses import dataclass


@dataclass
class ProcessingConfig:
    """Configuration for email processing."""

    output_directory: str
    convert_excel: bool = False
    max_attachment_size: int = 10_000_000
    batch_size: int = 100
