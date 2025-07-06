"""
Processing recommendation engine for smart email processing decisions.

This module analyzes email content and attachments to provide intelligent
recommendations for processing profiles, settings, and optimizations.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path

from email_parser.core.scanner import ScanResult, AttachmentInfo, FileType, ComplexityLevel


class RecommendationLevel(Enum):
    """Recommendation importance levels."""
    CRITICAL = "critical"      # Must do for successful processing
    HIGH = "high"             # Strongly recommended
    MEDIUM = "medium"         # Good to have
    LOW = "low"              # Optional optimization


class RecommendationCategory(Enum):
    """Categories of recommendations."""
    PROFILE = "profile"        # Processing profile selection
    CONVERTER = "converter"    # Converter settings
    PERFORMANCE = "performance" # Performance optimizations
    SECURITY = "security"      # Security considerations
    API = "api"               # API configuration
    OUTPUT = "output"         # Output format recommendations


@dataclass
class Recommendation:
    """A processing recommendation."""
    category: RecommendationCategory
    level: RecommendationLevel
    title: str
    description: str
    rationale: str
    action: str
    settings: Dict[str, Any] = field(default_factory=dict)
    conditions: List[str] = field(default_factory=list)
    cost_estimate: Optional[float] = None  # In USD
    time_impact: Optional[str] = None  # e.g., "+30 seconds"
    
    def __str__(self) -> str:
        """String representation for display."""
        level_symbols = {
            RecommendationLevel.CRITICAL: "🔴",
            RecommendationLevel.HIGH: "🟡", 
            RecommendationLevel.MEDIUM: "🔵",
            RecommendationLevel.LOW: "⚪"
        }
        
        symbol = level_symbols.get(self.level, "◯")
        return f"{symbol} {self.title}: {self.description}"


class ProcessingRecommender:
    """Generates intelligent processing recommendations based on email content."""
    
    def __init__(self):
        """Initialize the recommendation engine."""
        # API availability tracking
        self.api_keys_available = {
            'mistralai': bool(os.environ.get('MISTRALAI_API_KEY')),
            'openai': bool(os.environ.get('OPENAI_API_KEY')),
            'anthropic': bool(os.environ.get('ANTHROPIC_API_KEY'))
        }
        
        # System capabilities
        self.system_memory_gb = self._estimate_available_memory()
        self.cpu_cores = os.cpu_count() or 1
        
    def generate_recommendations(
        self, 
        scan_result: ScanResult,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> List[Recommendation]:
        """
        Generate comprehensive processing recommendations.
        
        Args:
            scan_result: Results from email scanning
            user_preferences: User preferences and constraints
            
        Returns:
            List of recommendations sorted by priority
        """
        recommendations = []
        prefs = user_preferences or {}
        
        # Profile recommendations
        recommendations.extend(self._recommend_profile(scan_result, prefs))
        
        # Converter-specific recommendations
        recommendations.extend(self._recommend_pdf_settings(scan_result, prefs))
        recommendations.extend(self._recommend_docx_settings(scan_result, prefs))
        recommendations.extend(self._recommend_excel_settings(scan_result, prefs))
        
        # Performance recommendations
        recommendations.extend(self._recommend_performance_settings(scan_result, prefs))
        
        # Security recommendations
        recommendations.extend(self._recommend_security_settings(scan_result, prefs))
        
        # API configuration recommendations
        recommendations.extend(self._recommend_api_settings(scan_result, prefs))
        
        # Output format recommendations
        recommendations.extend(self._recommend_output_settings(scan_result, prefs))
        
        # Sort by priority and return
        return self._sort_recommendations(recommendations)
        
    def _recommend_profile(
        self, 
        scan_result: ScanResult, 
        preferences: Dict[str, Any]
    ) -> List[Recommendation]:
        """Recommend processing profiles based on content analysis."""
        recommendations = []
        
        # Analyze email characteristics
        has_complex_attachments = any(
            att.complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.VERY_COMPLEX]
            for att in scan_result.attachments
        )
        
        has_ai_relevant_content = any(
            att.file_type in [FileType.PDF, FileType.DOCX] and att.size_mb > 0.5
            for att in scan_result.attachments
        )
        
        total_size_mb = sum(att.size_mb for att in scan_result.attachments)
        
        # Profile recommendations based on complexity and content
        if scan_result.complexity_score < 2:
            recommendations.append(Recommendation(
                category=RecommendationCategory.PROFILE,
                level=RecommendationLevel.HIGH,
                title="Use 'Quick' Profile",
                description="Fast processing for simple emails with minimal attachments",
                rationale=f"Low complexity score ({scan_result.complexity_score:.1f}) suggests simple content",
                action="Select the 'quick' processing profile",
                settings={"profile": "quick"},
                time_impact="-50% processing time"
            ))
        elif scan_result.complexity_score > 7 or has_complex_attachments:
            if has_ai_relevant_content:
                recommendations.append(Recommendation(
                    category=RecommendationCategory.PROFILE,
                    level=RecommendationLevel.HIGH,
                    title="Use 'AI-Ready' Profile",
                    description="Optimized for AI/LLM processing with semantic chunking",
                    rationale=f"High complexity ({scan_result.complexity_score:.1f}) with AI-relevant content",
                    action="Select the 'ai_ready' processing profile",
                    settings={"profile": "ai_ready"},
                    time_impact="+20% processing time"
                ))
            else:
                recommendations.append(Recommendation(
                    category=RecommendationCategory.PROFILE,
                    level=RecommendationLevel.HIGH,
                    title="Use 'Comprehensive' Profile",
                    description="Full processing with all conversions enabled",
                    rationale=f"High complexity ({scan_result.complexity_score:.1f}) requires comprehensive processing",
                    action="Select the 'comprehensive' processing profile",
                    settings={"profile": "comprehensive"}
                ))
        else:
            recommendations.append(Recommendation(
                category=RecommendationCategory.PROFILE,
                level=RecommendationLevel.MEDIUM,
                title="Use 'Comprehensive' Profile",
                description="Balanced processing for moderate complexity content",
                rationale=f"Moderate complexity ({scan_result.complexity_score:.1f}) benefits from balanced approach",
                action="Select the 'comprehensive' processing profile",
                settings={"profile": "comprehensive"}
            ))
            
        # Archive mode for important documents
        if total_size_mb > 10 or any("important" in att.filename.lower() for att in scan_result.attachments):
            recommendations.append(Recommendation(
                category=RecommendationCategory.PROFILE,
                level=RecommendationLevel.MEDIUM,
                title="Consider 'Archive' Profile",
                description="Maximum quality preservation for important documents",
                rationale="Large or important documents benefit from archive-quality processing",
                action="Select the 'archive' processing profile for maximum quality",
                settings={"profile": "archive"},
                time_impact="+100% processing time"
            ))
            
        return recommendations
        
    def _recommend_pdf_settings(
        self, 
        scan_result: ScanResult, 
        preferences: Dict[str, Any]
    ) -> List[Recommendation]:
        """Recommend PDF processing settings."""
        recommendations = []
        
        pdf_attachments = [att for att in scan_result.attachments if att.file_type == FileType.PDF]
        
        if not pdf_attachments:
            return recommendations
            
        # API key requirement
        if not self.api_keys_available['mistralai']:
            recommendations.append(Recommendation(
                category=RecommendationCategory.API,
                level=RecommendationLevel.CRITICAL,
                title="MistralAI API Key Required",
                description="PDF conversion requires MistralAI API key for OCR processing",
                rationale="Found PDF attachments but no API key configured",
                action="Configure MISTRALAI_API_KEY environment variable",
                conditions=["PDF conversion enabled"]
            ))
            
        # Processing mode recommendations
        large_pdfs = [att for att in pdf_attachments if att.size_mb > 5]
        image_heavy_pdfs = [att for att in pdf_attachments if "image" in att.features]
        
        if large_pdfs:
            recommendations.append(Recommendation(
                category=RecommendationCategory.CONVERTER,
                level=RecommendationLevel.HIGH,
                title="Optimize PDF Processing for Large Files",
                description="Use 'text' extraction mode for faster processing of large PDFs",
                rationale=f"Found {len(large_pdfs)} large PDF(s) > 5MB",
                action="Set pdf_extraction_mode='text' for faster processing",
                settings={"pdf_extraction_mode": "text"},
                time_impact="-60% PDF processing time",
                cost_estimate=self._estimate_pdf_cost(large_pdfs, mode="text")
            ))
        elif image_heavy_pdfs:
            recommendations.append(Recommendation(
                category=RecommendationCategory.CONVERTER,
                level=RecommendationLevel.HIGH,
                title="Enable Full PDF Processing",
                description="Use 'all' extraction mode for PDFs with images and charts",
                rationale=f"Found {len(image_heavy_pdfs)} PDF(s) with visual content",
                action="Set pdf_extraction_mode='all' to extract text and images",
                settings={"pdf_extraction_mode": "all"},
                cost_estimate=self._estimate_pdf_cost(image_heavy_pdfs, mode="all")
            ))
            
        # Quality recommendations
        if any(att.complexity == ComplexityLevel.VERY_COMPLEX for att in pdf_attachments):
            recommendations.append(Recommendation(
                category=RecommendationCategory.CONVERTER,
                level=RecommendationLevel.MEDIUM,
                title="Use High-Quality PDF Settings",
                description="Enable maximum quality for complex PDF documents",
                rationale="Complex PDFs benefit from high-quality processing",
                action="Enable high-quality OCR settings",
                settings={"pdf_high_quality": True},
                time_impact="+50% PDF processing time"
            ))
            
        return recommendations
        
    def _recommend_docx_settings(
        self, 
        scan_result: ScanResult, 
        preferences: Dict[str, Any]
    ) -> List[Recommendation]:
        """Recommend DOCX processing settings."""
        recommendations = []
        
        docx_attachments = [att for att in scan_result.attachments if att.file_type == FileType.DOCX]
        
        if not docx_attachments:
            return recommendations
            
        large_docs = [att for att in docx_attachments if att.size_mb > 2]
        
        # Chunking recommendations
        if large_docs or preferences.get('ai_processing', False):
            recommendations.append(Recommendation(
                category=RecommendationCategory.CONVERTER,
                level=RecommendationLevel.HIGH,
                title="Enable AI-Ready Chunking",
                description="Split large documents into AI-friendly chunks",
                rationale="Large documents or AI processing preference detected",
                action="Enable DOCX chunking with semantic strategy",
                settings={
                    "docx_enable_chunking": True,
                    "docx_chunk_strategy": "semantic",
                    "docx_chunk_size": 2000
                }
            ))
            
        # Image extraction for documents with images
        docs_with_images = [att for att in docx_attachments if "images" in att.features]
        if docs_with_images:
            recommendations.append(Recommendation(
                category=RecommendationCategory.CONVERTER,
                level=RecommendationLevel.MEDIUM,
                title="Extract Images from Documents",
                description="Save embedded images for complete content preservation",
                rationale=f"Found {len(docs_with_images)} document(s) with embedded images",
                action="Enable DOCX image extraction",
                settings={"docx_extract_images": True}
            ))
            
        # Style preservation for formatted documents
        formatted_docs = [att for att in docx_attachments if "formatted_text" in att.features]
        if formatted_docs:
            recommendations.append(Recommendation(
                category=RecommendationCategory.CONVERTER,
                level=RecommendationLevel.LOW,
                title="Preserve Document Formatting",
                description="Maintain style information for formatted documents",
                rationale="Documents with complex formatting detected",
                action="Enable style preservation",
                settings={"docx_preserve_styles": True}
            ))
            
        return recommendations
        
    def _recommend_excel_settings(
        self, 
        scan_result: ScanResult, 
        preferences: Dict[str, Any]
    ) -> List[Recommendation]:
        """Recommend Excel processing settings."""
        recommendations = []
        
        excel_attachments = [att for att in scan_result.attachments if att.file_type == FileType.XLSX]
        
        if not excel_attachments:
            return recommendations
            
        # Basic conversion recommendation
        recommendations.append(Recommendation(
            category=RecommendationCategory.CONVERTER,
            level=RecommendationLevel.HIGH,
            title="Convert Excel to CSV",
            description="Convert spreadsheets to CSV format for easy data access",
            rationale=f"Found {len(excel_attachments)} Excel file(s)",
            action="Enable Excel to CSV conversion",
            settings={"convert_excel": True}
        ))
        
        # Multi-sheet handling
        large_excel = [att for att in excel_attachments if att.size_mb > 1]
        if large_excel:
            recommendations.append(Recommendation(
                category=RecommendationCategory.CONVERTER,
                level=RecommendationLevel.MEDIUM,
                title="Process All Excel Worksheets",
                description="Convert all worksheets in large Excel files",
                rationale="Large Excel files likely contain multiple important worksheets",
                action="Enable processing of all worksheets",
                settings={"excel_convert_all_sheets": True}
            ))
            
        return recommendations
        
    def _recommend_performance_settings(
        self, 
        scan_result: ScanResult, 
        preferences: Dict[str, Any]
    ) -> List[Recommendation]:
        """Recommend performance optimization settings."""
        recommendations = []
        
        total_size_mb = sum(att.size_mb for att in scan_result.attachments)
        attachment_count = len(scan_result.attachments)
        
        # Memory optimization
        if total_size_mb > 20:
            recommendations.append(Recommendation(
                category=RecommendationCategory.PERFORMANCE,
                level=RecommendationLevel.HIGH,
                title="Increase Memory Limit",
                description="Large attachments require more memory for processing",
                rationale=f"Total attachment size ({total_size_mb:.1f} MB) exceeds standard limits",
                action="Increase memory limit to 1GB",
                settings={"memory_limit_mb": 1024}
            ))
        elif total_size_mb > 50:
            recommendations.append(Recommendation(
                category=RecommendationCategory.PERFORMANCE,
                level=RecommendationLevel.CRITICAL,
                title="Configure High Memory Mode",
                description="Very large attachments need high memory configuration",
                rationale=f"Total attachment size ({total_size_mb:.1f} MB) requires high memory mode",
                action="Enable high memory mode and consider processing attachments individually",
                settings={"memory_limit_mb": 2048, "process_individually": True}
            ))
            
        # Parallel processing
        if attachment_count > 3 and self.cpu_cores > 2:
            recommendations.append(Recommendation(
                category=RecommendationCategory.PERFORMANCE,
                level=RecommendationLevel.MEDIUM,
                title="Enable Parallel Processing",
                description="Process multiple attachments simultaneously for faster results",
                rationale=f"Multiple attachments ({attachment_count}) on multi-core system ({self.cpu_cores} cores)",
                action="Enable parallel processing",
                settings={
                    "parallel_processing": True,
                    "max_workers": min(4, self.cpu_cores)
                },
                time_impact=f"-{min(50, attachment_count * 10)}% total processing time"
            ))
            
        return recommendations
        
    def _recommend_security_settings(
        self, 
        scan_result: ScanResult, 
        preferences: Dict[str, Any]
    ) -> List[Recommendation]:
        """Recommend security-related settings."""
        recommendations = []
        
        large_attachments = [att for att in scan_result.attachments if att.size_mb > 10]
        
        # Size limit warnings
        if large_attachments:
            recommendations.append(Recommendation(
                category=RecommendationCategory.SECURITY,
                level=RecommendationLevel.MEDIUM,
                title="Review Large Attachment Security",
                description="Large attachments may pose security risks",
                rationale=f"Found {len(large_attachments)} attachment(s) > 10MB",
                action="Verify attachment sources and scan for malware",
                conditions=["Large attachments present"]
            ))
            
        # Executable file warnings
        risky_extensions = {'.exe', '.scr', '.bat', '.com', '.pif', '.cmd'}
        risky_attachments = [
            att for att in scan_result.attachments 
            if Path(att.filename).suffix.lower() in risky_extensions
        ]
        
        if risky_attachments:
            recommendations.append(Recommendation(
                category=RecommendationCategory.SECURITY,
                level=RecommendationLevel.CRITICAL,
                title="Potentially Dangerous Attachments",
                description="Executable attachments detected - exercise extreme caution",
                rationale=f"Found {len(risky_attachments)} potentially executable file(s)",
                action="Scan attachments with antivirus before processing",
                conditions=["Executable files present"]
            ))
            
        return recommendations
        
    def _recommend_api_settings(
        self, 
        scan_result: ScanResult, 
        preferences: Dict[str, Any]
    ) -> List[Recommendation]:
        """Recommend API configuration settings."""
        recommendations = []
        
        pdf_attachments = [att for att in scan_result.attachments if att.file_type == FileType.PDF]
        
        # API cost optimization
        if pdf_attachments:
            total_cost = self._estimate_total_api_cost(scan_result)
            
            if total_cost > 0.10:  # More than 10 cents
                recommendations.append(Recommendation(
                    category=RecommendationCategory.API,
                    level=RecommendationLevel.MEDIUM,
                    title="API Cost Optimization",
                    description="Consider cost-effective processing options for large PDF processing",
                    rationale=f"Estimated API cost: ${total_cost:.2f}",
                    action="Review PDF extraction modes to optimize costs",
                    cost_estimate=total_cost
                ))
                
        return recommendations
        
    def _recommend_output_settings(
        self, 
        scan_result: ScanResult, 
        preferences: Dict[str, Any]
    ) -> List[Recommendation]:
        """Recommend output format settings."""
        recommendations = []
        
        # AI processing output format
        if preferences.get('ai_processing', False):
            recommendations.append(Recommendation(
                category=RecommendationCategory.OUTPUT,
                level=RecommendationLevel.HIGH,
                title="Optimize Output for AI Processing",
                description="Use markdown format and enable chunking for AI/LLM compatibility",
                rationale="AI processing preference detected",
                action="Configure markdown output with structured chunking",
                settings={
                    "output_format": "markdown",
                    "enable_chunking": True,
                    "clean_formatting": True
                }
            ))
            
        # Structured data output
        excel_attachments = [att for att in scan_result.attachments if att.file_type == FileType.XLSX]
        if excel_attachments:
            recommendations.append(Recommendation(
                category=RecommendationCategory.OUTPUT,
                level=RecommendationLevel.MEDIUM,
                title="Structured Data Output",
                description="Maintain data structure in Excel conversions",
                rationale="Spreadsheet data detected",
                action="Enable structured CSV output with metadata",
                settings={"preserve_structure": True, "include_metadata": True}
            ))
            
        return recommendations
        
    def _sort_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Sort recommendations by priority and category."""
        priority_order = {
            RecommendationLevel.CRITICAL: 0,
            RecommendationLevel.HIGH: 1,
            RecommendationLevel.MEDIUM: 2,
            RecommendationLevel.LOW: 3
        }
        
        category_order = {
            RecommendationCategory.API: 0,
            RecommendationCategory.SECURITY: 1,
            RecommendationCategory.PROFILE: 2,
            RecommendationCategory.CONVERTER: 3,
            RecommendationCategory.PERFORMANCE: 4,
            RecommendationCategory.OUTPUT: 5
        }
        
        return sorted(
            recommendations,
            key=lambda r: (priority_order[r.level], category_order[r.category])
        )
        
    def _estimate_available_memory(self) -> float:
        """Estimate available system memory in GB."""
        try:
            import psutil
            return psutil.virtual_memory().available / (1024**3)
        except ImportError:
            # Fallback estimate
            return 4.0
            
    def _estimate_pdf_cost(self, pdf_attachments: List[AttachmentInfo], mode: str = "all") -> float:
        """Estimate MistralAI API cost for PDF processing."""
        # Rough cost estimate: $0.001 per page
        total_pages = 0
        
        for att in pdf_attachments:
            if att.estimated_pages:
                total_pages += att.estimated_pages
            else:
                # Estimate based on file size (rough: 75KB per page)
                estimated_pages = max(1, int(att.size_bytes / (75 * 1024)))
                total_pages += estimated_pages
                
        # Different modes have different costs
        mode_multipliers = {
            "text": 0.5,
            "images": 1.5,
            "all": 1.0
        }
        
        multiplier = mode_multipliers.get(mode, 1.0)
        return total_pages * 0.001 * multiplier
        
    def _estimate_total_api_cost(self, scan_result: ScanResult) -> float:
        """Estimate total API costs for processing."""
        pdf_attachments = [att for att in scan_result.attachments if att.file_type == FileType.PDF]
        return self._estimate_pdf_cost(pdf_attachments)
        
    def get_recommendation_summary(self, recommendations: List[Recommendation]) -> Dict[str, Any]:
        """Get a summary of recommendations by category and level."""
        summary = {
            "total": len(recommendations),
            "by_level": {},
            "by_category": {},
            "estimated_cost": 0.0,
            "critical_issues": []
        }
        
        for rec in recommendations:
            # Count by level
            level_key = rec.level.value
            summary["by_level"][level_key] = summary["by_level"].get(level_key, 0) + 1
            
            # Count by category
            cat_key = rec.category.value
            summary["by_category"][cat_key] = summary["by_category"].get(cat_key, 0) + 1
            
            # Add to estimated cost
            if rec.cost_estimate:
                summary["estimated_cost"] += rec.cost_estimate
                
            # Track critical issues
            if rec.level == RecommendationLevel.CRITICAL:
                summary["critical_issues"].append(rec.title)
                
        return summary