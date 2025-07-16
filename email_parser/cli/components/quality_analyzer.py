"""
Conversion quality analysis components.

Provides quality assessment and validation for converted files.
"""

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import json
import re
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn


@dataclass
class QualityMetric:
    """Represents a quality metric."""
    name: str
    value: float  # 0.0 to 1.0 where 1.0 is perfect
    description: str
    details: Optional[str] = None


@dataclass
class QualityReport:
    """Complete quality report for a conversion."""
    file_path: Path
    converter_type: str
    overall_score: float
    metrics: List[QualityMetric]
    warnings: List[str]
    errors: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]


class ConversionQualityAnalyzer:
    """Analyzes and reports on conversion quality."""
    
    def __init__(self, console: Console):
        self.console = console
    
    async def analyze_conversion(self, original_path: Path, converted_path: Path, 
                               conversion_type: str, conversion_metadata: Optional[Dict] = None) -> QualityReport:
        """
        Analyze conversion quality and generate comprehensive report.
        
        Args:
            original_path: Path to original file
            converted_path: Path to converted file
            conversion_type: Type of conversion (pdf, docx, xlsx)
            conversion_metadata: Metadata from conversion process
            
        Returns:
            QualityReport with detailed analysis
        """
        metrics = []
        warnings = []
        errors = []
        recommendations = []
        
        try:
            # Check if converted file exists
            if not converted_path.exists():
                errors.append(f"Converted file not found: {converted_path}")
                return QualityReport(
                    file_path=original_path,
                    converter_type=conversion_type,
                    overall_score=0.0,
                    metrics=[],
                    warnings=warnings,
                    errors=errors,
                    recommendations=["Check conversion process for errors"],
                    metadata={}
                )
            
            # Analyze based on conversion type
            if conversion_type == 'pdf':
                metrics.extend(await self._analyze_pdf_conversion(original_path, converted_path, conversion_metadata))
            elif conversion_type == 'docx':
                metrics.extend(await self._analyze_docx_conversion(original_path, converted_path, conversion_metadata))
            elif conversion_type in ['xlsx', 'xls']:
                metrics.extend(await self._analyze_excel_conversion(original_path, converted_path, conversion_metadata))
            
            # General file metrics
            metrics.extend(await self._analyze_general_metrics(original_path, converted_path))
            
            # Calculate overall score
            overall_score = sum(m.value for m in metrics) / len(metrics) if metrics else 0.0
            
            # Generate recommendations
            recommendations.extend(self._generate_recommendations(metrics, conversion_type))
            
            return QualityReport(
                file_path=original_path,
                converter_type=conversion_type,
                overall_score=overall_score,
                metrics=metrics,
                warnings=warnings,
                errors=errors,
                recommendations=recommendations,
                metadata=conversion_metadata or {}
            )
            
        except Exception as e:
            errors.append(f"Quality analysis failed: {str(e)}")
            return QualityReport(
                file_path=original_path,
                converter_type=conversion_type,
                overall_score=0.0,
                metrics=[],
                warnings=warnings,
                errors=errors,
                recommendations=["Manual review recommended"],
                metadata={}
            )
    
    async def _analyze_pdf_conversion(self, original: Path, converted: Path, 
                                    metadata: Optional[Dict]) -> List[QualityMetric]:
        """Analyze PDF conversion quality."""
        metrics = []
        
        try:
            # Read converted content
            if converted.suffix.lower() == '.md':
                with open(converted, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                # Try to read as text
                with open(converted, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
            # Text extraction quality
            text_quality = self._assess_text_quality(content)
            metrics.append(QualityMetric(
                name="Text Quality",
                value=text_quality,
                description="Quality of extracted text content",
                details=f"Content length: {len(content)} characters"
            ))
            
            # OCR confidence (if available in metadata)
            if metadata and 'ocr_confidence' in metadata:
                confidence = metadata['ocr_confidence']
                metrics.append(QualityMetric(
                    name="OCR Confidence",
                    value=confidence / 100.0,  # Assuming confidence is 0-100
                    description="OCR recognition confidence",
                    details=f"Average confidence: {confidence}%"
                ))
            
            # Image extraction success
            if metadata and 'images_extracted' in metadata:
                image_count = metadata.get('images_extracted', 0)
                total_images = metadata.get('total_images', image_count)
                
                if total_images > 0:
                    image_success = image_count / total_images
                else:
                    image_success = 1.0
                
                metrics.append(QualityMetric(
                    name="Image Extraction",
                    value=image_success,
                    description="Success rate of image extraction",
                    details=f"{image_count}/{total_images} images extracted"
                ))
            
            # Page processing success
            if metadata and 'pages_processed' in metadata:
                pages_processed = metadata['pages_processed']
                total_pages = metadata.get('total_pages', pages_processed)
                
                if total_pages > 0:
                    page_success = pages_processed / total_pages
                else:
                    page_success = 1.0
                
                metrics.append(QualityMetric(
                    name="Page Processing",
                    value=page_success,
                    description="Success rate of page processing",
                    details=f"{pages_processed}/{total_pages} pages processed"
                ))
            
        except Exception as e:
            metrics.append(QualityMetric(
                name="Analysis Error",
                value=0.0,
                description="Error during quality analysis",
                details=str(e)
            ))
        
        return metrics
    
    async def _analyze_docx_conversion(self, original: Path, converted: Path, 
                                     metadata: Optional[Dict]) -> List[QualityMetric]:
        """Analyze DOCX conversion quality."""
        metrics = []
        
        try:
            # Read converted content
            if converted.suffix.lower() == '.md':
                with open(converted, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                with open(converted, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
            # Text extraction quality
            text_quality = self._assess_text_quality(content)
            metrics.append(QualityMetric(
                name="Text Quality",
                value=text_quality,
                description="Quality of extracted text content",
                details=f"Content length: {len(content)} characters"
            ))
            
            # Metadata extraction completeness
            if metadata and 'metadata_extracted' in metadata:
                meta_items = metadata['metadata_extracted']
                expected_meta = ['title', 'author', 'created', 'modified']
                completeness = len([m for m in expected_meta if m in meta_items]) / len(expected_meta)
                
                metrics.append(QualityMetric(
                    name="Metadata Completeness",
                    value=completeness,
                    description="Completeness of metadata extraction",
                    details=f"Extracted: {', '.join(meta_items.keys()) if isinstance(meta_items, dict) else str(meta_items)}"
                ))
            
            # Style preservation
            style_indicators = ['**', '*', '#', '|']  # Bold, italic, headers, tables
            style_count = sum(content.count(indicator) for indicator in style_indicators)
            
            if style_count > 0:
                style_score = min(style_count / 100, 1.0)  # Normalize to reasonable scale
            else:
                style_score = 0.5  # Neutral score for documents without formatting
            
            metrics.append(QualityMetric(
                name="Style Preservation",
                value=style_score,
                description="Preservation of document formatting",
                details=f"Formatting indicators found: {style_count}"
            ))
            
            # Image extraction (if enabled)
            if metadata and 'images_extracted' in metadata:
                image_count = metadata.get('images_extracted', 0)
                total_images = metadata.get('total_images', image_count)
                
                if total_images > 0:
                    image_success = image_count / total_images
                else:
                    image_success = 1.0
                
                metrics.append(QualityMetric(
                    name="Image Extraction",
                    value=image_success,
                    description="Success rate of image extraction",
                    details=f"{image_count}/{total_images} images extracted"
                ))
            
            # Chunking quality (if chunking was performed)
            if metadata and 'chunks_created' in metadata:
                chunk_count = metadata['chunks_created']
                if chunk_count > 0:
                    # Simple heuristic: more chunks with reasonable content is better
                    avg_chunk_size = len(content) / chunk_count if chunk_count > 0 else 0
                    optimal_size = 2000  # Target chunk size
                    
                    if avg_chunk_size > 0:
                        chunk_quality = min(optimal_size / abs(avg_chunk_size - optimal_size + 1), 1.0)
                    else:
                        chunk_quality = 0.0
                    
                    metrics.append(QualityMetric(
                        name="Chunking Quality",
                        value=chunk_quality,
                        description="Quality of document chunking",
                        details=f"{chunk_count} chunks, avg size: {avg_chunk_size:.0f} chars"
                    ))
            
        except Exception as e:
            metrics.append(QualityMetric(
                name="Analysis Error",
                value=0.0,
                description="Error during quality analysis",
                details=str(e)
            ))
        
        return metrics
    
    async def _analyze_excel_conversion(self, original: Path, converted: Path, 
                                      metadata: Optional[Dict]) -> List[QualityMetric]:
        """Analyze Excel conversion quality."""
        metrics = []
        
        try:
            # For Excel, converted file is typically CSV
            with open(converted, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Data integrity check
            lines = content.strip().split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            
            data_integrity = len(non_empty_lines) / len(lines) if lines else 0.0
            
            metrics.append(QualityMetric(
                name="Data Integrity",
                value=data_integrity,
                description="Proportion of non-empty data rows",
                details=f"{len(non_empty_lines)}/{len(lines)} non-empty rows"
            ))
            
            # Structure preservation (CSV format validation)
            if lines:
                # Check if rows have consistent column counts
                column_counts = []
                for line in lines[:10]:  # Check first 10 lines
                    if line.strip():
                        column_counts.append(len(line.split(',')))
                
                if column_counts:
                    consistency = column_counts.count(max(set(column_counts), key=column_counts.count)) / len(column_counts)
                else:
                    consistency = 0.0
                
                metrics.append(QualityMetric(
                    name="Structure Consistency",
                    value=consistency,
                    description="Consistency of row/column structure",
                    details=f"Column counts: {set(column_counts)}"
                ))
            
            # Sheet processing (if metadata available)
            if metadata and 'sheets_processed' in metadata:
                sheets_processed = metadata['sheets_processed']
                total_sheets = metadata.get('total_sheets', sheets_processed)
                
                if total_sheets > 0:
                    sheet_success = sheets_processed / total_sheets
                else:
                    sheet_success = 1.0
                
                metrics.append(QualityMetric(
                    name="Sheet Processing",
                    value=sheet_success,
                    description="Success rate of sheet processing",
                    details=f"{sheets_processed}/{total_sheets} sheets processed"
                ))
            
        except Exception as e:
            metrics.append(QualityMetric(
                name="Analysis Error",
                value=0.0,
                description="Error during quality analysis",
                details=str(e)
            ))
        
        return metrics
    
    async def _analyze_general_metrics(self, original: Path, converted: Path) -> List[QualityMetric]:
        """Analyze general conversion metrics."""
        metrics = []
        
        try:
            # File size comparison
            original_size = original.stat().st_size
            converted_size = converted.stat().st_size
            
            # For text conversions, converted files are typically smaller
            # Score based on reasonable size ratio
            if original_size > 0:
                size_ratio = converted_size / original_size
                
                # Optimal ratio depends on file type, but generally 0.1-0.5 is reasonable for text extraction
                if 0.05 <= size_ratio <= 2.0:
                    size_score = 1.0
                elif size_ratio < 0.05:
                    size_score = max(0.0, size_ratio / 0.05)
                else:
                    size_score = max(0.0, 2.0 / size_ratio)
            else:
                size_score = 0.0
            
            metrics.append(QualityMetric(
                name="File Size Ratio",
                value=size_score,
                description="Reasonableness of converted file size",
                details=f"Original: {original_size:,} bytes, Converted: {converted_size:,} bytes"
            ))
            
            # File accessibility
            try:
                with open(converted, 'r', encoding='utf-8') as f:
                    f.read(100)  # Try to read first 100 characters
                accessibility = 1.0
            except Exception:
                accessibility = 0.0
            
            metrics.append(QualityMetric(
                name="File Accessibility",
                value=accessibility,
                description="Whether converted file can be read",
                details="File is readable" if accessibility > 0 else "File cannot be read"
            ))
            
        except Exception as e:
            metrics.append(QualityMetric(
                name="General Analysis Error",
                value=0.0,
                description="Error during general quality analysis",
                details=str(e)
            ))
        
        return metrics
    
    def _assess_text_quality(self, content: str) -> float:
        """Assess the quality of extracted text."""
        if not content.strip():
            return 0.0
        
        # Various quality indicators
        factors = []
        
        # Length factor (reasonable content length)
        length_score = min(len(content) / 1000, 1.0)  # Normalize to 1000 chars
        factors.append(length_score)
        
        # Character diversity (more diverse = better extraction)
        unique_chars = len(set(content.lower()))
        diversity_score = min(unique_chars / 50, 1.0)  # Normalize to 50 unique chars
        factors.append(diversity_score)
        
        # Word count (reasonable word extraction)
        words = content.split()
        word_score = min(len(words) / 100, 1.0)  # Normalize to 100 words
        factors.append(word_score)
        
        # Avoid too many repeated characters (indication of OCR errors)
        repeated_chars = sum(1 for i in range(len(content) - 2) if content[i] == content[i+1] == content[i+2])
        repeat_score = max(0.0, 1.0 - (repeated_chars / len(content)))
        factors.append(repeat_score)
        
        # Average the factors
        return sum(factors) / len(factors)
    
    def _generate_recommendations(self, metrics: List[QualityMetric], conversion_type: str) -> List[str]:
        """Generate recommendations based on quality metrics."""
        recommendations = []
        
        # Find low-scoring metrics
        low_quality_metrics = [m for m in metrics if m.value < 0.7]
        
        for metric in low_quality_metrics:
            if metric.name == "Text Quality":
                recommendations.append("Consider using different OCR settings or manual review for text extraction")
            elif metric.name == "OCR Confidence":
                recommendations.append("Low OCR confidence detected - consider higher quality scan or different extraction mode")
            elif metric.name == "Image Extraction":
                recommendations.append("Some images failed to extract - check image quality and format compatibility")
            elif metric.name == "Style Preservation":
                recommendations.append("Document formatting may not be fully preserved - review converted output")
            elif metric.name == "Data Integrity":
                recommendations.append("Some data rows appear empty - verify Excel conversion settings")
            elif metric.name == "Structure Consistency":
                recommendations.append("Inconsistent table structure detected - manual review recommended")
        
        # Type-specific recommendations
        if conversion_type == 'pdf':
            overall_score = sum(m.value for m in metrics) / len(metrics) if metrics else 0.0
            if overall_score < 0.6:
                recommendations.append("Consider using 'all' extraction mode for better PDF processing")
        
        elif conversion_type == 'docx':
            style_metrics = [m for m in metrics if m.name == "Style Preservation"]
            if style_metrics and style_metrics[0].value < 0.5:
                recommendations.append("Enable style extraction for better formatting preservation")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Conversion quality appears good - no specific issues detected")
        
        return recommendations
    
    def display_quality_report(self, report: QualityReport) -> None:
        """Display a formatted quality report."""
        # Overall score panel
        score_color = "green" if report.overall_score >= 0.8 else "yellow" if report.overall_score >= 0.6 else "red"
        score_text = f"[{score_color}]{report.overall_score:.1%}[/{score_color}]"
        
        header = f"""
[bold]Quality Report: {report.file_path.name}[/bold]
Converter: {report.converter_type.upper()}
Overall Score: {score_text}
"""
        
        self.console.print(Panel(header, title="📊 Conversion Quality Report"))
        
        # Metrics table
        if report.metrics:
            table = Table(title="Quality Metrics", show_header=True)
            table.add_column("Metric", style="cyan")
            table.add_column("Score", justify="center", width=8)
            table.add_column("Description", style="white")
            table.add_column("Details", style="dim")
            
            for metric in report.metrics:
                score_color = "green" if metric.value >= 0.8 else "yellow" if metric.value >= 0.6 else "red"
                score_text = f"[{score_color}]{metric.value:.1%}[/{score_color}]"
                
                table.add_row(
                    metric.name,
                    score_text,
                    metric.description,
                    metric.details or ""
                )
            
            self.console.print(table)
        
        # Warnings and errors
        if report.warnings:
            warning_text = "\n".join(f"• {w}" for w in report.warnings)
            self.console.print(Panel(warning_text, title="⚠️ Warnings", border_style="yellow"))
        
        if report.errors:
            error_text = "\n".join(f"• {e}" for e in report.errors)
            self.console.print(Panel(error_text, title="❌ Errors", border_style="red"))
        
        # Recommendations
        if report.recommendations:
            rec_text = "\n".join(f"• {r}" for r in report.recommendations)
            self.console.print(Panel(rec_text, title="💡 Recommendations", border_style="blue"))
    
    async def analyze_batch_quality(self, conversion_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze quality across a batch of conversions."""
        if not conversion_results:
            return {}
        
        # Collect all quality reports
        quality_reports = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Analyzing conversion quality...", total=len(conversion_results))
            
            for result in conversion_results:
                if result.get('success') and result.get('output_path'):
                    try:
                        report = await self.analyze_conversion(
                            Path(result['input_path']),
                            Path(result['output_path']),
                            result.get('converter_type', 'unknown'),
                            result.get('metadata')
                        )
                        quality_reports.append(report)
                    except Exception:
                        # Skip failed analyses
                        pass
                
                progress.advance(task)
        
        if not quality_reports:
            return {"message": "No quality reports generated"}
        
        # Calculate batch statistics
        overall_scores = [r.overall_score for r in quality_reports]
        
        batch_analysis = {
            "total_files": len(conversion_results),
            "analyzed_files": len(quality_reports),
            "average_quality": sum(overall_scores) / len(overall_scores),
            "high_quality_files": len([s for s in overall_scores if s >= 0.8]),
            "medium_quality_files": len([s for s in overall_scores if 0.6 <= s < 0.8]),
            "low_quality_files": len([s for s in overall_scores if s < 0.6]),
            "quality_by_type": {},
            "common_issues": []
        }
        
        # Quality by conversion type
        type_scores = {}
        for report in quality_reports:
            conv_type = report.converter_type
            if conv_type not in type_scores:
                type_scores[conv_type] = []
            type_scores[conv_type].append(report.overall_score)
        
        for conv_type, scores in type_scores.items():
            batch_analysis["quality_by_type"][conv_type] = {
                "average": sum(scores) / len(scores),
                "count": len(scores)
            }
        
        # Find common issues
        all_recommendations = []
        for report in quality_reports:
            all_recommendations.extend(report.recommendations)
        
        # Count recommendation frequency
        rec_counts = {}
        for rec in all_recommendations:
            rec_counts[rec] = rec_counts.get(rec, 0) + 1
        
        # Top 5 most common recommendations
        batch_analysis["common_issues"] = sorted(rec_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return batch_analysis