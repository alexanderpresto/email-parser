"""Style extraction and preservation for DOCX documents."""

import logging
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from docx import Document
    from docx.shared import RGBColor, Pt
    from docx.enum.style import WD_STYLE_TYPE
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    Document = None
    RGBColor = None
    Pt = None
    WD_STYLE_TYPE = None
    WD_ALIGN_PARAGRAPH = None
    logging.warning("python-docx not installed. Style extraction will be limited.")


class StyleType(Enum):
    """Types of styles in a document."""
    PARAGRAPH = "paragraph"
    CHARACTER = "character"
    TABLE = "table"
    LIST = "list"


@dataclass
class FontStyle:
    """Font styling information."""
    name: Optional[str] = None
    size: Optional[float] = None  # in points
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None
    strike: Optional[bool] = None
    color: Optional[str] = None  # hex color
    highlight: Optional[str] = None  # highlight color
    
    def to_css(self) -> Dict[str, str]:
        """Convert to CSS properties."""
        css = {}
        if self.name:
            css['font-family'] = self.name
        if self.size:
            css['font-size'] = f"{self.size}pt"
        if self.bold:
            css['font-weight'] = 'bold'
        if self.italic:
            css['font-style'] = 'italic'
        if self.underline:
            css['text-decoration'] = 'underline'
        if self.strike:
            css['text-decoration'] = 'line-through' if not self.underline else 'underline line-through'
        if self.color:
            css['color'] = self.color
        if self.highlight:
            css['background-color'] = self.highlight
        return css


@dataclass
class ParagraphStyle:
    """Paragraph styling information."""
    alignment: Optional[str] = None  # left, right, center, justify
    indent_left: Optional[float] = None  # in points
    indent_right: Optional[float] = None
    indent_first_line: Optional[float] = None
    space_before: Optional[float] = None
    space_after: Optional[float] = None
    line_spacing: Optional[float] = None  # multiplier (1.0 = single)
    keep_together: Optional[bool] = None
    keep_with_next: Optional[bool] = None
    page_break_before: Optional[bool] = None
    
    def to_css(self) -> Dict[str, str]:
        """Convert to CSS properties."""
        css = {}
        if self.alignment:
            css['text-align'] = self.alignment
        if self.indent_left:
            css['margin-left'] = f"{self.indent_left}pt"
        if self.indent_right:
            css['margin-right'] = f"{self.indent_right}pt"
        if self.indent_first_line:
            css['text-indent'] = f"{self.indent_first_line}pt"
        if self.space_before:
            css['margin-top'] = f"{self.space_before}pt"
        if self.space_after:
            css['margin-bottom'] = f"{self.space_after}pt"
        if self.line_spacing:
            css['line-height'] = str(self.line_spacing)
        return css


@dataclass
class StyleDefinition:
    """Complete style definition."""
    name: str
    style_id: str
    style_type: StyleType
    base_style: Optional[str] = None
    font: Optional[FontStyle] = None
    paragraph: Optional[ParagraphStyle] = None
    is_builtin: bool = False
    is_custom: bool = False
    priority: Optional[int] = None
    hidden: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = {
            'name': self.name,
            'style_id': self.style_id,
            'style_type': self.style_type.value,
            'is_builtin': self.is_builtin,
            'is_custom': self.is_custom,
            'hidden': self.hidden
        }
        
        if self.base_style:
            data['base_style'] = self.base_style
        if self.priority is not None:
            data['priority'] = self.priority
        if self.font:
            data['font'] = asdict(self.font)
        if self.paragraph:
            data['paragraph'] = asdict(self.paragraph)
            
        return data


@dataclass
class DocumentStyles:
    """Collection of all document styles."""
    paragraph_styles: Dict[str, StyleDefinition] = field(default_factory=dict)
    character_styles: Dict[str, StyleDefinition] = field(default_factory=dict)
    table_styles: Dict[str, StyleDefinition] = field(default_factory=dict)
    list_styles: Dict[str, StyleDefinition] = field(default_factory=dict)
    default_style: Optional[str] = None
    
    def get_all_styles(self) -> List[StyleDefinition]:
        """Get all styles as a flat list."""
        all_styles = []
        all_styles.extend(self.paragraph_styles.values())
        all_styles.extend(self.character_styles.values())
        all_styles.extend(self.table_styles.values())
        all_styles.extend(self.list_styles.values())
        return all_styles
    
    def get_used_styles(self, used_style_ids: Set[str]) -> List[StyleDefinition]:
        """Get only styles that are actually used in the document."""
        used_styles = []
        for style in self.get_all_styles():
            if style.style_id in used_style_ids:
                used_styles.append(style)
        return used_styles


class StyleExtractor:
    """Extract styles from DOCX documents."""
    
    def __init__(self):
        """Initialize style extractor."""
        self.logger = logging.getLogger(__name__)
    
    def extract_styles(self, file_path: str) -> DocumentStyles:
        """Extract all styles from document."""
        if not Document:
            self.logger.warning("python-docx not available for style extraction")
            return DocumentStyles()
        
        try:
            doc = Document(file_path)
            return self._extract_document_styles(doc)
        except Exception as e:
            self.logger.error(f"Error extracting styles: {e}")
            return DocumentStyles()
    
    def extract_used_styles(self, file_path: str) -> DocumentStyles:
        """Extract only styles that are actually used in the document."""
        if not Document:
            return DocumentStyles()
        
        try:
            doc = Document(file_path)
            used_style_ids = self._find_used_styles(doc)
            styles = self._extract_document_styles(doc)
            
            # Filter to only used styles
            filtered = DocumentStyles()
            for style_id in used_style_ids:
                if style_id in styles.paragraph_styles:
                    filtered.paragraph_styles[style_id] = styles.paragraph_styles[style_id]
                elif style_id in styles.character_styles:
                    filtered.character_styles[style_id] = styles.character_styles[style_id]
                elif style_id in styles.table_styles:
                    filtered.table_styles[style_id] = styles.table_styles[style_id]
                elif style_id in styles.list_styles:
                    filtered.list_styles[style_id] = styles.list_styles[style_id]
            
            filtered.default_style = styles.default_style
            return filtered
            
        except Exception as e:
            self.logger.error(f"Error extracting used styles: {e}")
            return DocumentStyles()
    
    def _extract_document_styles(self, doc: Any) -> DocumentStyles:
        """Extract all style definitions from document."""
        doc_styles = DocumentStyles()
        
        if not hasattr(doc, 'styles'):
            return doc_styles
        
        try:
            # Get default style
            for style in doc.styles:
                if hasattr(style, 'type') and style.type == WD_STYLE_TYPE.PARAGRAPH:
                    if hasattr(style, 'base_style') and style.base_style is None:
                        if hasattr(style, 'style_id'):
                            doc_styles.default_style = style.style_id
                            break
            
            # Extract all styles
            for style in doc.styles:
                if not hasattr(style, 'style_id') or not hasattr(style, 'name'):
                    continue
                
                style_def = self._extract_style_definition(style)
                if style_def:
                    # Categorize by type
                    if style_def.style_type == StyleType.PARAGRAPH:
                        doc_styles.paragraph_styles[style_def.style_id] = style_def
                    elif style_def.style_type == StyleType.CHARACTER:
                        doc_styles.character_styles[style_def.style_id] = style_def
                    elif style_def.style_type == StyleType.TABLE:
                        doc_styles.table_styles[style_def.style_id] = style_def
                    elif style_def.style_type == StyleType.LIST:
                        doc_styles.list_styles[style_def.style_id] = style_def
                        
        except Exception as e:
            self.logger.warning(f"Error processing document styles: {e}")
        
        return doc_styles
    
    def _extract_style_definition(self, style: Any) -> Optional[StyleDefinition]:
        """Extract a single style definition."""
        try:
            # Determine style type
            style_type = StyleType.PARAGRAPH  # default
            if hasattr(style, 'type'):
                if style.type == WD_STYLE_TYPE.CHARACTER:
                    style_type = StyleType.CHARACTER
                elif style.type == WD_STYLE_TYPE.TABLE:
                    style_type = StyleType.TABLE
                elif style.type == WD_STYLE_TYPE.LIST:
                    style_type = StyleType.LIST
            
            # Create style definition
            style_def = StyleDefinition(
                name=style.name,
                style_id=style.style_id,
                style_type=style_type,
                is_builtin=getattr(style, 'builtin', False),
                is_custom=not getattr(style, 'builtin', False),
                hidden=getattr(style, 'hidden', False),
                priority=getattr(style, 'priority', None)
            )
            
            # Extract base style
            if hasattr(style, 'base_style') and style.base_style:
                style_def.base_style = style.base_style.style_id
            
            # Extract font properties
            if hasattr(style, 'font'):
                style_def.font = self._extract_font_style(style.font)
            
            # Extract paragraph properties
            if style_type == StyleType.PARAGRAPH and hasattr(style, 'paragraph_format'):
                style_def.paragraph = self._extract_paragraph_style(style.paragraph_format)
            
            return style_def
            
        except Exception as e:
            self.logger.debug(f"Error extracting style {getattr(style, 'name', 'unknown')}: {e}")
            return None
    
    def _extract_font_style(self, font: Any) -> FontStyle:
        """Extract font styling information."""
        font_style = FontStyle()
        
        try:
            if hasattr(font, 'name') and font.name:
                font_style.name = font.name
            if hasattr(font, 'size') and font.size:
                font_style.size = font.size.pt if hasattr(font.size, 'pt') else None
            if hasattr(font, 'bold'):
                font_style.bold = font.bold
            if hasattr(font, 'italic'):
                font_style.italic = font.italic
            if hasattr(font, 'underline'):
                font_style.underline = font.underline
            if hasattr(font, 'strike'):
                font_style.strike = font.strike
            if hasattr(font, 'color') and hasattr(font.color, 'rgb') and font.color.rgb:
                # Convert RGB to hex
                rgb = font.color.rgb
                font_style.color = f"#{rgb.red:02x}{rgb.green:02x}{rgb.blue:02x}"
        except Exception as e:
            self.logger.debug(f"Error extracting font style: {e}")
        
        return font_style
    
    def _extract_paragraph_style(self, para_format: Any) -> ParagraphStyle:
        """Extract paragraph styling information."""
        para_style = ParagraphStyle()
        
        try:
            # Alignment
            if hasattr(para_format, 'alignment') and para_format.alignment:
                alignment_map = {
                    WD_ALIGN_PARAGRAPH.LEFT: 'left',
                    WD_ALIGN_PARAGRAPH.CENTER: 'center',
                    WD_ALIGN_PARAGRAPH.RIGHT: 'right',
                    WD_ALIGN_PARAGRAPH.JUSTIFY: 'justify'
                }
                para_style.alignment = alignment_map.get(para_format.alignment, None)
            
            # Indentation
            if hasattr(para_format, 'left_indent') and para_format.left_indent:
                para_style.indent_left = para_format.left_indent.pt
            if hasattr(para_format, 'right_indent') and para_format.right_indent:
                para_style.indent_right = para_format.right_indent.pt
            if hasattr(para_format, 'first_line_indent') and para_format.first_line_indent:
                para_style.indent_first_line = para_format.first_line_indent.pt
            
            # Spacing
            if hasattr(para_format, 'space_before') and para_format.space_before:
                para_style.space_before = para_format.space_before.pt
            if hasattr(para_format, 'space_after') and para_format.space_after:
                para_style.space_after = para_format.space_after.pt
            if hasattr(para_format, 'line_spacing'):
                para_style.line_spacing = para_format.line_spacing
            
            # Other properties
            if hasattr(para_format, 'keep_together'):
                para_style.keep_together = para_format.keep_together
            if hasattr(para_format, 'keep_with_next'):
                para_style.keep_with_next = para_format.keep_with_next
            if hasattr(para_format, 'page_break_before'):
                para_style.page_break_before = para_format.page_break_before
                
        except Exception as e:
            self.logger.debug(f"Error extracting paragraph style: {e}")
        
        return para_style
    
    def _find_used_styles(self, doc: Any) -> Set[str]:
        """Find all style IDs actually used in the document."""
        used_styles = set()
        
        try:
            # Check paragraph styles
            for para in doc.paragraphs:
                if hasattr(para, 'style') and hasattr(para.style, 'style_id'):
                    used_styles.add(para.style.style_id)
                
                # Check character styles in runs
                for run in para.runs:
                    if hasattr(run, 'style') and run.style and hasattr(run.style, 'style_id'):
                        used_styles.add(run.style.style_id)
            
            # Check table styles
            for table in doc.tables:
                if hasattr(table, 'style') and hasattr(table.style, 'style_id'):
                    used_styles.add(table.style.style_id)
                    
        except Exception as e:
            self.logger.debug(f"Error finding used styles: {e}")
        
        return used_styles


class StyleConverter:
    """Convert extracted styles to various formats."""
    
    @staticmethod
    def to_css(styles: DocumentStyles, prefix: str = "docx") -> str:
        """Convert document styles to CSS."""
        css_lines = []
        
        # Convert paragraph styles
        for style_id, style_def in styles.paragraph_styles.items():
            css_class = f".{prefix}-{style_id.replace(' ', '-').lower()}"
            css_props = {}
            
            if style_def.font:
                css_props.update(style_def.font.to_css())
            if style_def.paragraph:
                css_props.update(style_def.paragraph.to_css())
            
            if css_props:
                css_lines.append(f"{css_class} {{")
                for prop, value in css_props.items():
                    css_lines.append(f"  {prop}: {value};")
                css_lines.append("}")
        
        # Convert character styles
        for style_id, style_def in styles.character_styles.items():
            css_class = f".{prefix}-{style_id.replace(' ', '-').lower()}"
            if style_def.font:
                css_props = style_def.font.to_css()
                if css_props:
                    css_lines.append(f"{css_class} {{")
                    for prop, value in css_props.items():
                        css_lines.append(f"  {prop}: {value};")
                    css_lines.append("}")
        
        return "\n".join(css_lines)
    
    @staticmethod
    def to_style_map(styles: DocumentStyles) -> Dict[str, Dict[str, Any]]:
        """Convert to a simplified style mapping."""
        style_map = {}
        
        for style in styles.get_all_styles():
            style_data = {}
            
            if style.font:
                font_data = asdict(style.font)
                # Remove None values
                style_data['font'] = {k: v for k, v in font_data.items() if v is not None}
            
            if style.paragraph:
                para_data = asdict(style.paragraph)
                # Remove None values
                style_data['paragraph'] = {k: v for k, v in para_data.items() if v is not None}
            
            if style_data:
                style_data['type'] = style.style_type.value
                style_data['name'] = style.name
                style_map[style.style_id] = style_data
        
        return style_map