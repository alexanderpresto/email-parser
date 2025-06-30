"""Tests for DOCX style extraction."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from email_parser.converters.docx.style_extractor import (
    StyleType,
    FontStyle,
    ParagraphStyle,
    StyleDefinition,
    DocumentStyles,
    StyleExtractor,
    StyleConverter
)


class TestFontStyle:
    """Test FontStyle dataclass."""
    
    def test_default_values(self):
        """Test default font style values."""
        font = FontStyle()
        assert font.name is None
        assert font.size is None
        assert font.bold is None
        assert font.color is None
    
    def test_to_css_basic(self):
        """Test basic CSS conversion."""
        font = FontStyle(
            name="Arial",
            size=12.0,
            bold=True,
            italic=True
        )
        
        css = font.to_css()
        
        assert css['font-family'] == "Arial"
        assert css['font-size'] == "12.0pt"
        assert css['font-weight'] == "bold"
        assert css['font-style'] == "italic"
    
    def test_to_css_with_decorations(self):
        """Test CSS with text decorations."""
        font = FontStyle(underline=True, strike=True)
        css = font.to_css()
        assert css['text-decoration'] == "underline line-through"
        
        font2 = FontStyle(strike=True)
        css2 = font2.to_css()
        assert css2['text-decoration'] == "line-through"
    
    def test_to_css_with_colors(self):
        """Test CSS with colors."""
        font = FontStyle(
            color="#FF0000",
            highlight="#FFFF00"
        )
        
        css = font.to_css()
        assert css['color'] == "#FF0000"
        assert css['background-color'] == "#FFFF00"


class TestParagraphStyle:
    """Test ParagraphStyle dataclass."""
    
    def test_default_values(self):
        """Test default paragraph style values."""
        para = ParagraphStyle()
        assert para.alignment is None
        assert para.indent_left is None
        assert para.line_spacing is None
    
    def test_to_css(self):
        """Test CSS conversion."""
        para = ParagraphStyle(
            alignment="center",
            indent_left=36.0,
            indent_right=18.0,
            space_before=12.0,
            space_after=6.0,
            line_spacing=1.5
        )
        
        css = para.to_css()
        
        assert css['text-align'] == "center"
        assert css['margin-left'] == "36.0pt"
        assert css['margin-right'] == "18.0pt"
        assert css['margin-top'] == "12.0pt"
        assert css['margin-bottom'] == "6.0pt"
        assert css['line-height'] == "1.5"


class TestStyleDefinition:
    """Test StyleDefinition dataclass."""
    
    def test_creation(self):
        """Test style definition creation."""
        style = StyleDefinition(
            name="Heading 1",
            style_id="Heading1",
            style_type=StyleType.PARAGRAPH,
            is_builtin=True
        )
        
        assert style.name == "Heading 1"
        assert style.style_id == "Heading1"
        assert style.style_type == StyleType.PARAGRAPH
        assert style.is_builtin is True
        assert style.is_custom is False
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        font = FontStyle(name="Arial", size=16.0, bold=True)
        para = ParagraphStyle(alignment="center")
        
        style = StyleDefinition(
            name="Custom Style",
            style_id="CustomStyle",
            style_type=StyleType.PARAGRAPH,
            font=font,
            paragraph=para,
            priority=10
        )
        
        data = style.to_dict()
        
        assert data['name'] == "Custom Style"
        assert data['style_id'] == "CustomStyle"
        assert data['style_type'] == "paragraph"
        assert data['priority'] == 10
        assert 'font' in data
        assert data['font']['name'] == "Arial"
        assert 'paragraph' in data
        assert data['paragraph']['alignment'] == "center"


class TestDocumentStyles:
    """Test DocumentStyles collection."""
    
    def test_initialization(self):
        """Test document styles initialization."""
        styles = DocumentStyles()
        assert len(styles.paragraph_styles) == 0
        assert len(styles.character_styles) == 0
        assert styles.default_style is None
    
    def test_get_all_styles(self):
        """Test getting all styles."""
        styles = DocumentStyles()
        
        # Add some styles
        para_style = StyleDefinition("Para", "para1", StyleType.PARAGRAPH)
        char_style = StyleDefinition("Char", "char1", StyleType.CHARACTER)
        
        styles.paragraph_styles["para1"] = para_style
        styles.character_styles["char1"] = char_style
        
        all_styles = styles.get_all_styles()
        assert len(all_styles) == 2
        assert para_style in all_styles
        assert char_style in all_styles
    
    def test_get_used_styles(self):
        """Test filtering to used styles."""
        styles = DocumentStyles()
        
        # Add styles
        style1 = StyleDefinition("Used", "used1", StyleType.PARAGRAPH)
        style2 = StyleDefinition("Unused", "unused1", StyleType.PARAGRAPH)
        
        styles.paragraph_styles["used1"] = style1
        styles.paragraph_styles["unused1"] = style2
        
        # Get only used styles
        used = styles.get_used_styles({"used1"})
        assert len(used) == 1
        assert used[0].style_id == "used1"


class TestStyleExtractor:
    """Test style extraction functionality."""
    
    def test_initialization(self):
        """Test extractor initialization."""
        extractor = StyleExtractor()
        assert hasattr(extractor, 'logger')
    
    @patch('email_parser.converters.docx.style_extractor.Document', None)
    def test_extract_without_python_docx(self):
        """Test extraction when python-docx is not available."""
        extractor = StyleExtractor()
        styles = extractor.extract_styles("fake.docx")
        
        assert isinstance(styles, DocumentStyles)
        assert len(styles.paragraph_styles) == 0
    
    @patch('email_parser.converters.docx.style_extractor.Document')
    @patch('email_parser.converters.docx.style_extractor.WD_STYLE_TYPE')
    def test_extract_paragraph_style(self, mock_style_type, mock_document_class):
        """Test extracting paragraph style."""
        # Setup mocks
        mock_style_type.PARAGRAPH = 1
        mock_style_type.CHARACTER = 2
        
        mock_style = Mock()
        mock_style.name = "Normal"
        mock_style.style_id = "Normal"
        mock_style.type = 1  # PARAGRAPH
        mock_style.builtin = True
        mock_style.hidden = False
        mock_style.priority = 0
        mock_style.base_style = None
        
        # Mock font
        mock_font = Mock()
        mock_font.name = "Calibri"
        mock_font.size = Mock(pt=11.0)
        mock_font.bold = False
        mock_font.italic = False
        mock_font.underline = False
        mock_font.strike = False
        mock_font.color = Mock(rgb=None)
        mock_style.font = mock_font
        
        # Mock paragraph format
        mock_para_format = Mock()
        mock_para_format.alignment = None
        mock_para_format.left_indent = None
        mock_para_format.right_indent = None
        mock_para_format.first_line_indent = None
        mock_para_format.space_before = None
        mock_para_format.space_after = None
        mock_para_format.line_spacing = 1.15
        mock_para_format.keep_together = False
        mock_para_format.keep_with_next = False
        mock_para_format.page_break_before = False
        mock_style.paragraph_format = mock_para_format
        
        mock_doc = Mock()
        mock_doc.styles = [mock_style]
        mock_doc.paragraphs = []
        mock_doc.tables = []
        
        mock_document_class.return_value = mock_doc
        
        extractor = StyleExtractor()
        styles = extractor.extract_styles("test.docx")
        
        assert "Normal" in styles.paragraph_styles
        normal_style = styles.paragraph_styles["Normal"]
        assert normal_style.name == "Normal"
        assert normal_style.is_builtin is True
        assert normal_style.font.name == "Calibri"
        assert normal_style.font.size == 11.0
    
    @patch('email_parser.converters.docx.style_extractor.Document')
    def test_find_used_styles(self, mock_document_class):
        """Test finding used styles in document."""
        # Create mock paragraph with style
        mock_para = Mock()
        mock_para.style = Mock(style_id="Heading1")
        
        # Create mock run with style
        mock_run = Mock()
        mock_run.style = Mock(style_id="Emphasis")
        mock_para.runs = [mock_run]
        
        # Create mock table with style
        mock_table = Mock()
        mock_table.style = Mock(style_id="TableGrid")
        
        mock_doc = Mock()
        mock_doc.paragraphs = [mock_para]
        mock_doc.tables = [mock_table]
        mock_doc.styles = []
        
        mock_document_class.return_value = mock_doc
        
        extractor = StyleExtractor()
        # Access private method for testing
        used_styles = extractor._find_used_styles(mock_doc)
        
        assert "Heading1" in used_styles
        assert "Emphasis" in used_styles
        assert "TableGrid" in used_styles


class TestStyleConverter:
    """Test style conversion functionality."""
    
    def test_to_css_paragraph_styles(self):
        """Test converting paragraph styles to CSS."""
        styles = DocumentStyles()
        
        # Add a paragraph style
        font = FontStyle(name="Arial", size=14.0, bold=True)
        para = ParagraphStyle(alignment="center", space_before=12.0)
        
        style_def = StyleDefinition(
            name="Heading 1",
            style_id="Heading1",
            style_type=StyleType.PARAGRAPH,
            font=font,
            paragraph=para
        )
        
        styles.paragraph_styles["Heading1"] = style_def
        
        css = StyleConverter.to_css(styles)
        
        assert ".docx-heading1" in css
        assert "font-family: Arial;" in css
        assert "font-size: 14.0pt;" in css
        assert "font-weight: bold;" in css
        assert "text-align: center;" in css
        assert "margin-top: 12.0pt;" in css
    
    def test_to_style_map(self):
        """Test converting to style map."""
        styles = DocumentStyles()
        
        # Add styles
        font = FontStyle(name="Times", size=12.0)
        style_def = StyleDefinition(
            name="Body Text",
            style_id="BodyText",
            style_type=StyleType.PARAGRAPH,
            font=font
        )
        
        styles.paragraph_styles["BodyText"] = style_def
        
        style_map = StyleConverter.to_style_map(styles)
        
        assert "BodyText" in style_map
        assert style_map["BodyText"]["name"] == "Body Text"
        assert style_map["BodyText"]["type"] == "paragraph"
        assert style_map["BodyText"]["font"]["name"] == "Times"
        assert style_map["BodyText"]["font"]["size"] == 12.0
        # None values should be filtered out
        assert "bold" not in style_map["BodyText"]["font"]