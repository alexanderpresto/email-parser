"""
Email content scanner for attachment detection and analysis.

This module provides functionality to scan email files and analyze their content,
including attachment detection, size analysis, and processing time estimation.
"""

import email
import mimetypes
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
from pathlib import Path
from typing import List, Set, Optional, Dict, Any
import logging
from email.message import Message

logger = logging.getLogger(__name__)


class FileType(Enum):
    """Supported file types for processing."""
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    IMAGE = "image"
    TEXT = "text"
    OTHER = "other"


class ComplexityLevel(Enum):
    """Document complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


@dataclass
class AttachmentInfo:
    """Information about an email attachment."""
    filename: str
    content_type: str
    size_bytes: int
    file_type: FileType
    complexity: ComplexityLevel
    features: Set[str] = field(default_factory=set)
    estimated_pages: Optional[int] = None
    processing_time_estimate: Optional[timedelta] = None
    warnings: List[str] = field(default_factory=list)

    @property
    def size_mb(self) -> float:
        """Get size in megabytes."""
        return self.size_bytes / (1024 * 1024)

    @property
    def size_display(self) -> str:
        """Get human-readable size display."""
        if self.size_bytes < 1024:
            return f"{self.size_bytes} B"
        elif self.size_bytes < 1024 * 1024:
            return f"{self.size_bytes / 1024:.1f} KB"
        else:
            return f"{self.size_mb:.1f} MB"


@dataclass
class ScanResult:
    """Results from email scanning."""
    email_path: Path
    subject: str
    sender: str
    date: Optional[str]
    size_bytes: int
    body_size_bytes: int
    attachments: List[AttachmentInfo]
    complexity_score: float
    estimated_time: timedelta
    recommendations: List[str]
    warnings: List[str]
    features: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_size_mb(self) -> float:
        """Get total size in megabytes."""
        return self.size_bytes / (1024 * 1024)

    @property
    def attachment_count(self) -> int:
        """Get number of attachments."""
        return len(self.attachments)

    @property
    def has_pdf(self) -> bool:
        """Check if email has PDF attachments."""
        return any(att.file_type == FileType.PDF for att in self.attachments)

    @property
    def has_docx(self) -> bool:
        """Check if email has DOCX attachments."""
        return any(att.file_type == FileType.DOCX for att in self.attachments)

    @property
    def has_excel(self) -> bool:
        """Check if email has Excel attachments."""
        return any(att.file_type == FileType.XLSX for att in self.attachments)


class EmailScanner:
    """Scans emails to detect attachments and analyze content."""

    # File extension mappings
    FILE_TYPE_MAPPING = {
        '.pdf': FileType.PDF,
        '.docx': FileType.DOCX,
        '.doc': FileType.DOCX,
        '.xlsx': FileType.XLSX,
        '.xls': FileType.XLSX,
        '.png': FileType.IMAGE,
        '.jpg': FileType.IMAGE,
        '.jpeg': FileType.IMAGE,
        '.gif': FileType.IMAGE,
        '.bmp': FileType.IMAGE,
        '.txt': FileType.TEXT,
        '.csv': FileType.TEXT,
        '.md': FileType.TEXT,
    }

    # Processing time estimates per MB (in seconds)
    PROCESSING_TIME_PER_MB = {
        FileType.PDF: 30,  # OCR is slow
        FileType.DOCX: 5,
        FileType.XLSX: 3,
        FileType.IMAGE: 2,
        FileType.TEXT: 1,
        FileType.OTHER: 1,
    }

    def __init__(self):
        """Initialize the email scanner."""
        self.mime_types = mimetypes.MimeTypes()

    def scan(self, email_path: Path) -> ScanResult:
        """
        Perform comprehensive email scan.
        
        Args:
            email_path: Path to the email file
            
        Returns:
            ScanResult containing analysis details
            
        Raises:
            FileNotFoundError: If email file doesn't exist
            ValueError: If email file is invalid
        """
        if not email_path.exists():
            raise FileNotFoundError(f"Email file not found: {email_path}")

        try:
            with open(email_path, 'rb') as f:
                msg = email.message_from_binary_file(f)
        except Exception as e:
            raise ValueError(f"Invalid email file: {e}")

        # Extract basic info
        subject = msg.get('Subject', 'No Subject')
        sender = msg.get('From', 'Unknown')
        date = msg.get('Date', None)
        
        # Get file size
        size_bytes = email_path.stat().st_size
        
        # Scan attachments
        attachments = self._scan_attachments(msg)
        
        # Calculate body size
        body_size = self._get_body_size(msg)
        
        # Calculate complexity and estimates
        complexity_score = self._calculate_complexity(attachments, body_size)
        estimated_time = self._estimate_processing_time(attachments)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(attachments, complexity_score)
        
        # Collect warnings
        warnings = self._collect_warnings(attachments, size_bytes)
        
        # Additional features
        features = self._extract_features(msg, attachments)
        
        return ScanResult(
            email_path=email_path,
            subject=subject,
            sender=sender,
            date=date,
            size_bytes=size_bytes,
            body_size_bytes=body_size,
            attachments=attachments,
            complexity_score=complexity_score,
            estimated_time=estimated_time,
            recommendations=recommendations,
            warnings=warnings,
            features=features
        )

    def _scan_attachments(self, msg: Message) -> List[AttachmentInfo]:
        """Scan all attachments in the email."""
        attachments = []
        
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
                
            if part.get('Content-Disposition') is None:
                continue
                
            filename = part.get_filename()
            if not filename:
                continue
                
            # Get attachment info
            content_type = part.get_content_type()
            payload = part.get_payload(decode=True)
            # Ensure payload is bytes or None
            if payload is not None and not isinstance(payload, bytes):
                payload = None
            size_bytes = len(payload) if payload else 0
            
            # Determine file type
            file_extension = Path(filename).suffix.lower()
            file_type = self.FILE_TYPE_MAPPING.get(file_extension, FileType.OTHER)
            
            # Analyze complexity
            complexity = self._analyze_attachment_complexity(
                filename, file_type, size_bytes, payload
            )
            
            # Extract features
            features = self._extract_attachment_features(
                filename, file_type, payload
            )
            
            # Estimate processing time
            processing_time = self._estimate_attachment_time(file_type, size_bytes)
            
            # Collect warnings
            warnings = self._check_attachment_warnings(
                filename, file_type, size_bytes
            )
            
            attachment = AttachmentInfo(
                filename=filename,
                content_type=content_type,
                size_bytes=size_bytes,
                file_type=file_type,
                complexity=complexity,
                features=features,
                processing_time_estimate=processing_time,
                warnings=warnings
            )
            
            # Add page estimation for PDFs
            if file_type == FileType.PDF:
                attachment.estimated_pages = self._estimate_pdf_pages(size_bytes)
            
            attachments.append(attachment)
            
        return attachments

    def _get_body_size(self, msg: Message) -> int:
        """Calculate the size of email body text."""
        body_size = 0
        
        for part in msg.walk():
            if part.get_content_type() in ['text/plain', 'text/html']:
                payload = part.get_payload(decode=True)
                if payload:
                    body_size += len(payload)
                    
        return body_size

    def _analyze_attachment_complexity(
        self, 
        filename: str, 
        file_type: FileType, 
        size_bytes: int,
        payload: Optional[bytes]
    ) -> ComplexityLevel:
        """Analyze the complexity of an attachment."""
        # Size-based complexity
        size_mb = size_bytes / (1024 * 1024)
        
        if file_type == FileType.PDF:
            if size_mb < 1:
                return ComplexityLevel.SIMPLE
            elif size_mb < 5:
                return ComplexityLevel.MODERATE
            elif size_mb < 20:
                return ComplexityLevel.COMPLEX
            else:
                return ComplexityLevel.VERY_COMPLEX
                
        elif file_type == FileType.DOCX:
            if size_mb < 0.5:
                return ComplexityLevel.SIMPLE
            elif size_mb < 2:
                return ComplexityLevel.MODERATE
            elif size_mb < 10:
                return ComplexityLevel.COMPLEX
            else:
                return ComplexityLevel.VERY_COMPLEX
                
        elif file_type == FileType.XLSX:
            if size_mb < 0.1:
                return ComplexityLevel.SIMPLE
            elif size_mb < 1:
                return ComplexityLevel.MODERATE
            elif size_mb < 5:
                return ComplexityLevel.COMPLEX
            else:
                return ComplexityLevel.VERY_COMPLEX
                
        else:
            if size_mb < 1:
                return ComplexityLevel.SIMPLE
            elif size_mb < 5:
                return ComplexityLevel.MODERATE
            else:
                return ComplexityLevel.COMPLEX

    def _extract_attachment_features(
        self, 
        filename: str, 
        file_type: FileType,
        payload: Optional[bytes]
    ) -> Set[str]:
        """Extract features from attachment for better recommendations."""
        features = set()
        
        # Basic features based on file type
        if file_type == FileType.PDF:
            features.add("document")
            # Could analyze PDF structure if needed
            
        elif file_type == FileType.DOCX:
            features.add("document")
            features.add("formatted_text")
            
        elif file_type == FileType.XLSX:
            features.add("spreadsheet")
            features.add("structured_data")
            
        elif file_type == FileType.IMAGE:
            features.add("visual_content")
            
        # Add more sophisticated feature detection here
        # This is a placeholder for more advanced analysis
        
        return features

    def _estimate_attachment_time(
        self, 
        file_type: FileType, 
        size_bytes: int
    ) -> timedelta:
        """Estimate processing time for an attachment."""
        size_mb = size_bytes / (1024 * 1024)
        seconds_per_mb = self.PROCESSING_TIME_PER_MB.get(file_type, 1)
        
        # Minimum processing time
        min_seconds = 1
        
        # Calculate time with overhead
        estimated_seconds = max(min_seconds, size_mb * seconds_per_mb)
        
        # Add startup overhead
        if file_type == FileType.PDF:
            estimated_seconds += 5  # OCR startup time
            
        return timedelta(seconds=int(estimated_seconds))

    def _check_attachment_warnings(
        self, 
        filename: str, 
        file_type: FileType, 
        size_bytes: int
    ) -> List[str]:
        """Check for potential issues with attachment."""
        warnings = []
        size_mb = size_bytes / (1024 * 1024)
        
        # Size warnings
        if size_mb > 50:
            warnings.append(f"Large file size ({size_mb:.1f} MB) may take longer to process")
        
        # Type-specific warnings
        if file_type == FileType.PDF and size_mb > 20:
            warnings.append("Large PDF may require significant OCR processing time")
            
        if file_type == FileType.XLSX and size_mb > 10:
            warnings.append("Large spreadsheet may have memory requirements")
            
        # Filename warnings
        if len(filename) > 255:
            warnings.append("Very long filename may cause issues")
            
        return warnings

    def _estimate_pdf_pages(self, size_bytes: int) -> int:
        """Estimate number of pages in a PDF based on size."""
        # Rough estimation: average page is 50-100KB
        size_kb = size_bytes / 1024
        estimated_pages = int(size_kb / 75)  # Use 75KB as average
        return max(1, estimated_pages)

    def _calculate_complexity(
        self, 
        attachments: List[AttachmentInfo], 
        body_size: int
    ) -> float:
        """Calculate overall email complexity score (0-10)."""
        score = 0.0
        
        # Body complexity (up to 1 point)
        body_kb = body_size / 1024
        if body_kb < 10:
            score += 0.2
        elif body_kb < 50:
            score += 0.5
        else:
            score += 1.0
            
        # Attachment count (up to 2 points)
        att_count = len(attachments)
        if att_count > 0:
            score += min(2.0, att_count * 0.5)
            
        # Attachment complexity (up to 4 points)
        if attachments:
            complexity_points = {
                ComplexityLevel.SIMPLE: 0.5,
                ComplexityLevel.MODERATE: 1.0,
                ComplexityLevel.COMPLEX: 2.0,
                ComplexityLevel.VERY_COMPLEX: 3.0
            }
            
            max_complexity = max(
                complexity_points.get(att.complexity, 0) 
                for att in attachments
            )
            score += max_complexity
            
        # File type diversity (up to 2 points)
        file_types = {att.file_type for att in attachments}
        score += min(2.0, len(file_types) * 0.5)
        
        # Total size impact (up to 1 point)
        total_mb = sum(att.size_mb for att in attachments)
        if total_mb > 10:
            score += 0.5
        if total_mb > 50:
            score += 0.5
            
        return min(10.0, score)

    def _estimate_processing_time(
        self, 
        attachments: List[AttachmentInfo]
    ) -> timedelta:
        """Estimate total processing time."""
        if not attachments:
            return timedelta(seconds=5)  # Basic email processing
            
        # Sum individual estimates
        total_seconds = 5  # Base time for email parsing
        
        for attachment in attachments:
            if attachment.processing_time_estimate:
                total_seconds += attachment.processing_time_estimate.total_seconds()
                
        # Add overhead for multiple files
        if len(attachments) > 1:
            total_seconds += len(attachments) * 2
            
        return timedelta(seconds=int(total_seconds))

    def _generate_recommendations(
        self, 
        attachments: List[AttachmentInfo], 
        complexity_score: float
    ) -> List[str]:
        """Generate processing recommendations based on scan results."""
        recommendations = []
        
        # Profile recommendations based on complexity
        if complexity_score < 3:
            recommendations.append("Use 'quick' profile for fast processing")
        elif complexity_score < 6:
            recommendations.append("Use 'comprehensive' profile for balanced processing")
        else:
            recommendations.append("Use 'ai_ready' profile for complex document processing")
            
        # PDF recommendations
        pdf_attachments = [a for a in attachments if a.file_type == FileType.PDF]
        if pdf_attachments:
            large_pdfs = [a for a in pdf_attachments if a.size_mb > 5]
            if large_pdfs:
                recommendations.append("Enable MistralAI OCR for large PDFs")
                recommendations.append("Consider 'text' mode for faster PDF processing")
            else:
                recommendations.append("Enable PDF conversion with 'all' mode")
                
        # DOCX recommendations
        docx_attachments = [a for a in attachments if a.file_type == FileType.DOCX]
        if docx_attachments:
            recommendations.append("Enable DOCX conversion with AI-ready chunking")
            if any(a.size_mb > 2 for a in docx_attachments):
                recommendations.append("Use semantic chunking for large documents")
                
        # Excel recommendations
        excel_attachments = [a for a in attachments if a.file_type == FileType.XLSX]
        if excel_attachments:
            recommendations.append("Enable Excel to CSV conversion")
            
        # Performance recommendations
        total_size = sum(a.size_mb for a in attachments)
        if total_size > 20:
            recommendations.append("Consider increasing memory limit for large files")
            
        if len(attachments) > 5:
            recommendations.append("Enable parallel processing for multiple attachments")
            
        return recommendations

    def _collect_warnings(
        self, 
        attachments: List[AttachmentInfo], 
        total_size: int
    ) -> List[str]:
        """Collect all warnings from scan."""
        warnings = []
        
        # Size warning
        total_mb = total_size / (1024 * 1024)
        if total_mb > 100:
            warnings.append(f"Large email size ({total_mb:.1f} MB) may require extra processing time")
            
        # Attachment warnings
        for attachment in attachments:
            warnings.extend(attachment.warnings)
            
        # API requirement warnings
        if any(a.file_type == FileType.PDF for a in attachments):
            warnings.append("PDF conversion requires MistralAI API key")
            
        return warnings

    def _extract_features(
        self, 
        msg: Message, 
        attachments: List[AttachmentInfo]
    ) -> Dict[str, Any]:
        """Extract additional features for advanced analysis."""
        features = {
            'has_html_body': False,
            'has_text_body': False,
            'attachment_types': list({a.file_type.value for a in attachments}),
            'total_attachments': len(attachments),
            'encoding': msg.get_content_charset(),
            'content_transfer_encoding': msg.get('Content-Transfer-Encoding', ''),
        }
        
        # Check body types
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                features['has_html_body'] = True
            elif part.get_content_type() == 'text/plain':
                features['has_text_body'] = True
                
        return features