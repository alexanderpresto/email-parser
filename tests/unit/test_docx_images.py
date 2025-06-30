"""Tests for DOCX image extraction."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
from io import BytesIO
import hashlib

from email_parser.converters.docx.image_handler import (
    ImageInfo,
    ExtractedImage,
    ImageHandler,
    ImageManifest
)


class TestImageInfo:
    """Test ImageInfo dataclass."""
    
    def test_creation(self):
        """Test image info creation."""
        info = ImageInfo(
            image_id="rId1",
            original_name="image1.jpg",
            content_type="image/jpeg",
            width=800,
            height=600,
            file_size=50000,
            hash="abc123",
            alt_text="Test image"
        )
        
        assert info.image_id == "rId1"
        assert info.original_name == "image1.jpg"
        assert info.width == 800
        assert info.height == 600
        assert info.alt_text == "Test image"
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        info = ImageInfo(
            image_id="rId2",
            original_name="image2.png",
            content_type="image/png",
            width=400,
            height=300,
            file_size=25000,
            hash="def456",
            paragraph_index=5,
            run_index=2
        )
        
        data = info.to_dict()
        
        assert data['image_id'] == "rId2"
        assert data['width'] == 400
        assert data['paragraph_index'] == 5
        assert data['alt_text'] is None


class TestExtractedImage:
    """Test ExtractedImage functionality."""
    
    def test_creation(self):
        """Test extracted image creation."""
        info = ImageInfo(
            image_id="rId1",
            original_name="test.jpg",
            content_type="image/jpeg",
            width=100,
            height=100,
            file_size=1000,
            hash="test_hash"
        )
        
        data = b"fake image data"
        img = ExtractedImage(info=info, data=data)
        
        assert img.info.image_id == "rId1"
        assert img.data == data
        assert img.pil_image is None
    
    def test_to_base64(self):
        """Test base64 conversion."""
        info = ImageInfo(
            image_id="rId1",
            original_name="test.jpg",
            content_type="image/jpeg",
            width=100,
            height=100,
            file_size=1000,
            hash="test_hash"
        )
        
        data = b"test data"
        img = ExtractedImage(info=info, data=data)
        
        base64_str = img.to_base64()
        assert base64_str == "dGVzdCBkYXRh"  # base64 of "test data"
    
    @patch('email_parser.converters.docx.image_handler.Image', None)
    def test_save_without_pil(self, tmp_path):
        """Test saving image without PIL."""
        info = ImageInfo(
            image_id="rId1",
            original_name="test.jpg",
            content_type="image/jpeg",
            width=100,
            height=100,
            file_size=1000,
            hash="test_hash"
        )
        
        data = b"fake image data"
        img = ExtractedImage(info=info, data=data)
        
        saved_path = img.save(tmp_path)
        
        assert saved_path.exists()
        assert saved_path.name == "test.jpg"
        assert saved_path.read_bytes() == data


class TestImageHandler:
    """Test image extraction functionality."""
    
    def test_initialization(self):
        """Test handler initialization."""
        handler = ImageHandler(extract_quality=90, max_dimension=1200)
        
        assert handler.extract_quality == 90
        assert handler.max_dimension == 1200
        assert hasattr(handler, 'logger')
    
    @patch('email_parser.converters.docx.image_handler.Document', None)
    def test_extract_without_python_docx(self):
        """Test extraction when python-docx is not available."""
        handler = ImageHandler()
        images = handler.extract_images("fake.docx")
        
        assert images == []
    
    @patch('email_parser.converters.docx.image_handler.Document')
    def test_extract_images_basic(self, mock_document_class):
        """Test basic image extraction."""
        # Create mock document
        mock_doc = Mock()
        mock_doc.part = Mock()
        mock_doc.part.rels = Mock()
        mock_doc.part.rels.values.return_value = []
        mock_doc.paragraphs = []
        mock_doc.tables = []
        
        mock_document_class.return_value = mock_doc
        
        handler = ImageHandler()
        images = handler.extract_images("test.docx")
        
        assert isinstance(images, list)
    
    def test_get_extension_from_content_type(self):
        """Test file extension mapping."""
        handler = ImageHandler()
        
        assert handler._get_extension_from_content_type("image/jpeg") == ".jpg"
        assert handler._get_extension_from_content_type("image/png") == ".png"
        assert handler._get_extension_from_content_type("image/gif") == ".gif"
        assert handler._get_extension_from_content_type("unknown/type") == ".bin"
    
    @patch('email_parser.converters.docx.image_handler.Document')
    def test_extract_with_inline_images(self, mock_document_class):
        """Test extraction of inline images."""
        # Create mock image relationship
        mock_rel = Mock()
        mock_rel.rId = "rId1"
        mock_rel.reltype = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
        mock_rel.target_part = Mock()
        mock_rel.target_part.blob = b"fake image data"
        mock_rel.target_part.content_type = "image/jpeg"
        
        # Create mock element with inline image
        mock_element = Mock()
        mock_drawing = Mock()
        mock_blip = Mock()
        mock_blip.get.return_value = "rId1"  # embed ID
        
        mock_element.xpath.side_effect = lambda query: {
            './/w:drawing': [mock_drawing],
        }.get(query, [])
        
        mock_drawing.xpath.return_value = [mock_blip]
        
        # Create mock run with element
        mock_run = Mock()
        mock_run._element = mock_element
        
        # Create mock paragraph
        mock_para = Mock()
        mock_para.runs = [mock_run]
        mock_para._element = Mock()
        
        # Create mock document
        mock_doc = Mock()
        mock_doc.part = Mock()
        mock_doc.part.rels = Mock()
        mock_doc.part.rels.values.return_value = [mock_rel]
        mock_doc.part.package = Mock()
        mock_doc.part.package.parts = []
        mock_doc.paragraphs = [mock_para]
        mock_doc.tables = []
        
        mock_document_class.return_value = mock_doc
        
        handler = ImageHandler()
        # Access private method for testing
        image_parts = handler._get_image_parts(mock_doc)
        
        assert "rId1" in image_parts
        assert image_parts["rId1"][0] == "image/jpeg"
        assert image_parts["rId1"][1] == b"fake image data"
    
    def test_process_image(self):
        """Test image processing."""
        handler = ImageHandler()
        
        image_data = ("image/png", b"fake png data")
        processed = handler._process_image(image_data, "rId1", para_idx=0, run_idx=1)
        
        assert processed is not None
        assert processed.info.image_id == "rId1"
        assert processed.info.content_type == "image/png"
        assert processed.info.original_name == "image_rId1.png"
        assert processed.info.file_size == len(b"fake png data")
        assert processed.info.paragraph_index == 0
        assert processed.info.run_index == 1
        
        # Check hash
        expected_hash = hashlib.sha256(b"fake png data").hexdigest()
        assert processed.info.hash == expected_hash
    
    @patch('email_parser.converters.docx.image_handler.Document')
    def test_extract_and_save_images(self, mock_document_class, tmp_path):
        """Test extracting and saving images to directory."""
        # Setup mock document
        mock_doc = Mock()
        mock_doc.part = Mock()
        mock_doc.part.rels = Mock()
        mock_doc.part.rels.values.return_value = []
        mock_doc.paragraphs = []
        mock_doc.tables = []
        
        mock_document_class.return_value = mock_doc
        
        handler = ImageHandler()
        saved = handler.extract_and_save_images("test.docx", tmp_path)
        
        assert isinstance(saved, dict)


class TestImageManifest:
    """Test image manifest functionality."""
    
    def test_create_manifest(self):
        """Test manifest creation."""
        # Create test images
        images = []
        for i in range(3):
            info = ImageInfo(
                image_id=f"rId{i}",
                original_name=f"image{i}.jpg",
                content_type="image/jpeg",
                width=800,
                height=600,
                file_size=10000 * (i + 1),
                hash=f"hash{i}",
                paragraph_index=i,
                run_index=0
            )
            img = ExtractedImage(info=info, data=b"fake data")
            images.append(img)
        
        manifest = ImageManifest.create_manifest(images)
        
        assert manifest['total_images'] == 3
        assert manifest['total_size'] == 60000  # 10000 + 20000 + 30000
        assert manifest['unique_images'] == 3
        assert len(manifest['images']) == 3
        
        # Check location info
        assert manifest['images'][0]['location']['paragraph'] == 0
        assert manifest['images'][1]['location']['paragraph'] == 1
    
    def test_create_manifest_with_duplicates(self):
        """Test manifest with duplicate images."""
        images = []
        
        # Create two images with same hash
        for i in range(2):
            info = ImageInfo(
                image_id=f"rId{i}",
                original_name=f"image{i}.jpg",
                content_type="image/jpeg",
                width=800,
                height=600,
                file_size=10000,
                hash="same_hash",  # Same hash
                paragraph_index=i
            )
            img = ExtractedImage(info=info, data=b"same data")
            images.append(img)
        
        manifest = ImageManifest.create_manifest(images)
        
        assert manifest['total_images'] == 2
        assert manifest['unique_images'] == 1  # Only one unique hash
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_manifest(self, mock_json_dump, mock_file, tmp_path):
        """Test saving manifest to file."""
        manifest = {
            'total_images': 1,
            'images': [{'id': 'test'}]
        }
        
        ImageManifest.save_manifest(manifest, tmp_path)
        
        # Check file was opened correctly
        expected_path = tmp_path / 'image_manifest.json'
        mock_file.assert_called_once_with(expected_path, 'w', encoding='utf-8')
        
        # Check JSON was written
        mock_json_dump.assert_called_once()