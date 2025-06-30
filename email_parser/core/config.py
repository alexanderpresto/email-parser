from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import os
from pathlib import Path


@dataclass
class PDFConversionConfig:
    """Configuration for PDF to Markdown conversion."""
    
    enabled: bool = True
    api_key_env: str = "MISTRALAI_API_KEY"
    extraction_mode: str = "all"  # Options: text, images, all
    image_limit: int = 0  # 0 = no limit
    image_min_size: int = 100  # Minimum image size in pixels
    image_format: str = "png"  # Output format for images
    pagination_enabled: bool = True
    pagination_separator: str = "---"  # Page separator in Markdown
    cache_enabled: bool = True
    cache_directory: str = ".cache/pdf"
    cache_max_size_mb: int = 100
    api_timeout: int = 30  # API timeout in seconds
    api_max_retries: int = 3
    api_retry_delay: int = 1  # Initial retry delay in seconds


@dataclass
class ExcelConversionConfig:
    """Configuration for Excel to CSV conversion."""
    
    enabled: bool = True
    max_rows_per_sheet: int = 1_000_000
    include_formulas: bool = True
    preserve_formatting: bool = False


@dataclass
class DocxConversionConfig:
    """Configuration for DOCX to Markdown conversion."""
    
    enabled: bool = True
    max_file_size: int = 52428800  # 50MB
    output_format: str = "both"  # json, html, both
    extract_tables: bool = True
    
    # Week 2: AI-ready chunking features
    enable_chunking: bool = True  # Week 2 feature - ENABLED
    chunking_strategy: str = "hybrid"  # token, semantic, hybrid
    max_chunk_tokens: int = 2000
    chunk_overlap: int = 200
    preserve_structure: bool = True
    
    # Week 2: Enhanced metadata extraction
    extract_metadata: bool = True
    include_custom_properties: bool = True
    analyze_metadata: bool = True
    
    # Week 2: Style preservation system
    extract_styles: bool = True
    preserve_styles: bool = True
    style_output_format: str = "json"  # json, css
    include_comments: bool = True
    
    # Week 2: Advanced image handling
    extract_images: bool = True  # Week 2 feature - ENABLED
    image_quality: int = 85
    max_image_size: int = 1200
    generate_image_manifest: bool = True


@dataclass
class SecurityConfig:
    """Configuration for security settings."""
    
    max_attachment_size: int = 10_000_000  # 10MB
    allowed_extensions: List[str] = field(default_factory=lambda: [
        ".pdf", ".docx", ".xlsx", ".txt", ".jpg", ".png", ".csv", ".zip"
    ])
    enable_malware_scanning: bool = False
    validate_pdf_content: bool = True


@dataclass
class PerformanceConfig:
    """Configuration for performance settings."""
    
    chunk_size: int = 1_048_576  # 1MB
    enable_caching: bool = True
    cache_size: int = 100
    pdf_cache_size: int = 50
    use_memory_mapping: bool = True
    parallel_extraction: bool = True
    api_connection_pooling: bool = True
    max_workers: int = 4


@dataclass
class ErrorHandlingConfig:
    """Configuration for error handling."""
    
    mode: str = "graceful"  # Options: strict, graceful, permissive
    continue_on_error: bool = True
    max_retries: int = 3


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    enable_detailed_logging: bool = False
    log_file: Optional[str] = "email_parser.log"


@dataclass
class OutputConfig:
    """Configuration for output organization."""
    
    text_dir: str = "processed_text"
    attachments_dir: str = "attachments"
    inline_images_dir: str = "inline_images"
    excel_conversion_dir: str = "converted_excel"
    pdf_conversion_dir: str = "converted_pdf"
    docx_conversion_dir: str = "converted_docx"
    organize_by_date: bool = False
    date_format: str = "%Y/%m/%d"


@dataclass
class ProcessingConfig:
    """Comprehensive configuration for email processing.
    
    This configuration class provides all settings needed for email parsing,
    PDF conversion, Excel conversion, security, performance, and output organization.
    """

    # Core processing settings
    output_directory: str
    batch_size: int = 100
    
    # Conversion settings (backward compatibility)
    convert_excel: bool = True
    convert_pdf: bool = True
    convert_docx: bool = True
    
    # Legacy settings (for backward compatibility)
    max_attachment_size: int = 10_000_000
    
    # Comprehensive configuration objects
    pdf_conversion: PDFConversionConfig = field(default_factory=PDFConversionConfig)
    excel_conversion: ExcelConversionConfig = field(default_factory=ExcelConversionConfig)
    docx_conversion: DocxConversionConfig = field(default_factory=DocxConversionConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    error_handling: ErrorHandlingConfig = field(default_factory=ErrorHandlingConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    
    # PDF-specific convenience properties (for CLI and examples)
    pdf_extraction_mode: str = "all"
    pdf_image_limit: int = 0
    pdf_image_min_size: int = 100
    pdf_paginate: bool = True
    
    # DOCX-specific convenience properties (for CLI and examples)
    docx_extract_metadata: bool = True
    docx_extract_images: bool = True  # Week 2 - ENABLED
    docx_enable_chunking: bool = True  # Week 2 - ENABLED
    docx_chunk_size: int = 2000
    docx_chunk_overlap: int = 200
    docx_chunk_strategy: str = "hybrid"
    docx_extract_styles: bool = True
    docx_extract_comments: bool = True
    
    # General settings
    enable_detailed_logging: bool = False
    max_workers: int = 4
    
    def __post_init__(self):
        """Post-initialization to sync convenience properties with config objects."""
        # Sync PDF settings
        self.pdf_conversion.extraction_mode = self.pdf_extraction_mode
        self.pdf_conversion.image_limit = self.pdf_image_limit
        self.pdf_conversion.image_min_size = self.pdf_image_min_size
        self.pdf_conversion.pagination_enabled = self.pdf_paginate
        self.pdf_conversion.enabled = self.convert_pdf
        
        # Sync Excel settings
        self.excel_conversion.enabled = self.convert_excel
        
        # Sync DOCX settings
        self.docx_conversion.enabled = self.convert_docx
        self.docx_conversion.extract_metadata = self.docx_extract_metadata
        self.docx_conversion.extract_images = self.docx_extract_images
        self.docx_conversion.enable_chunking = self.docx_enable_chunking
        self.docx_conversion.max_chunk_tokens = self.docx_chunk_size
        self.docx_conversion.chunk_overlap = self.docx_chunk_overlap
        self.docx_conversion.chunking_strategy = self.docx_chunk_strategy
        self.docx_conversion.extract_styles = self.docx_extract_styles
        self.docx_conversion.include_comments = self.docx_extract_comments
        
        # Sync security settings
        self.security.max_attachment_size = self.max_attachment_size
        
        # Sync performance settings
        self.performance.max_workers = self.max_workers
        
        # Sync logging settings
        self.logging.enable_detailed_logging = self.enable_detailed_logging
        
        # Ensure output directory exists
        Path(self.output_directory).mkdir(parents=True, exist_ok=True)
    
    def get_api_key(self) -> Optional[str]:
        """Get the MistralAI API key from environment variables."""
        return os.environ.get(self.pdf_conversion.api_key_env)
    
    def is_pdf_conversion_available(self) -> bool:
        """Check if PDF conversion is enabled and API key is available."""
        return (
            self.pdf_conversion.enabled and 
            self.convert_pdf and 
            self.get_api_key() is not None
        )
    
    def get_output_paths(self) -> Dict[str, Path]:
        """Get all output directory paths."""
        base_path = Path(self.output_directory)
        return {
            'text': base_path / self.output.text_dir,
            'attachments': base_path / self.output.attachments_dir,
            'inline_images': base_path / self.output.inline_images_dir,
            'excel_conversion': base_path / self.output.excel_conversion_dir,
            'pdf_conversion': base_path / self.output.pdf_conversion_dir,
            'docx_conversion': base_path / self.output.docx_conversion_dir,
        }
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "ProcessingConfig":
        """Create configuration from YAML file.
        
        Args:
            yaml_path: Path to YAML configuration file
            
        Returns:
            ProcessingConfig instance
            
        Note:
            This method is a placeholder for future YAML configuration loading.
            Currently returns default configuration.
        """
        # TODO: Implement YAML configuration loading
        # For now, return default configuration
        return cls(output_directory="output")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format."""
        return {
            'processing': {
                'output_directory': self.output_directory,
                'convert_excel': self.convert_excel,
                'convert_pdf': self.convert_pdf,
                'convert_docx': self.convert_docx,
                'batch_size': self.batch_size,
                'max_workers': self.max_workers,
            },
            'security': {
                'max_attachment_size': self.security.max_attachment_size,
                'allowed_extensions': self.security.allowed_extensions,
                'enable_malware_scanning': self.security.enable_malware_scanning,
                'validate_pdf_content': self.security.validate_pdf_content,
            },
            'pdf_conversion': {
                'enabled': self.pdf_conversion.enabled,
                'extraction_mode': self.pdf_conversion.extraction_mode,
                'image_settings': {
                    'limit': self.pdf_conversion.image_limit,
                    'min_size': self.pdf_conversion.image_min_size,
                    'format': self.pdf_conversion.image_format,
                },
                'pagination': {
                    'enabled': self.pdf_conversion.pagination_enabled,
                    'separator': self.pdf_conversion.pagination_separator,
                },
                'cache': {
                    'enabled': self.pdf_conversion.cache_enabled,
                    'directory': self.pdf_conversion.cache_directory,
                    'max_size_mb': self.pdf_conversion.cache_max_size_mb,
                },
            },
            'excel_conversion': {
                'max_rows_per_sheet': self.excel_conversion.max_rows_per_sheet,
                'include_formulas': self.excel_conversion.include_formulas,
                'preserve_formatting': self.excel_conversion.preserve_formatting,
            },
            'docx_conversion': {
                'enabled': self.docx_conversion.enabled,
                'max_file_size': self.docx_conversion.max_file_size,
                'output_format': self.docx_conversion.output_format,
                'extract_tables': self.docx_conversion.extract_tables,
                'extract_metadata': self.docx_conversion.extract_metadata,
                'extract_images': self.docx_conversion.extract_images,
                'enable_chunking': self.docx_conversion.enable_chunking,
                'max_chunk_tokens': self.docx_conversion.max_chunk_tokens,
                'chunk_overlap': self.docx_conversion.chunk_overlap,
            },
            'output': {
                'text_dir': self.output.text_dir,
                'attachments_dir': self.output.attachments_dir,
                'inline_images_dir': self.output.inline_images_dir,
                'excel_conversion_dir': self.output.excel_conversion_dir,
                'pdf_conversion_dir': self.output.pdf_conversion_dir,
                'docx_conversion_dir': self.output.docx_conversion_dir,
                'organize_by_date': self.output.organize_by_date,
                'date_format': self.output.date_format,
            }
        }
