"""Image extraction and handling for DOCX documents."""

import logging
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from io import BytesIO
import hashlib

try:
    from docx import Document
    from docx.opc.constants import RELATIONSHIP_TYPE as RT
    from PIL import Image
except ImportError:
    Document = None
    RT = None
    Image = None
    logging.warning("python-docx or Pillow not installed. Image extraction will be limited.")


@dataclass
class ImageInfo:
    """Information about an extracted image."""
    image_id: str
    original_name: str
    content_type: str
    width: int
    height: int
    file_size: int
    hash: str  # SHA256 hash for deduplication
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    paragraph_index: Optional[int] = None
    run_index: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class ExtractedImage:
    """Extracted image with data and metadata."""
    info: ImageInfo
    data: bytes
    pil_image: Optional[Any] = None  # PIL Image object
    
    def save(self, output_path: Path, quality: int = 85) -> Path:
        """Save image to file."""
        file_path = output_path / self.info.original_name
        
        if self.pil_image and Image:
            # Save using PIL with quality control
            if self.info.content_type == 'image/jpeg':
                self.pil_image.save(str(file_path), 'JPEG', quality=quality, optimize=True)
            elif self.info.content_type == 'image/png':
                self.pil_image.save(str(file_path), 'PNG', optimize=True)
            else:
                self.pil_image.save(str(file_path))
        else:
            # Save raw bytes
            file_path.write_bytes(self.data)
        
        return file_path
    
    def to_base64(self) -> str:
        """Convert image data to base64 string."""
        return base64.b64encode(self.data).decode('utf-8')


class ImageHandler:
    """Handle image extraction from DOCX documents."""
    
    def __init__(self, extract_quality: int = 85, max_dimension: Optional[int] = None):
        """Initialize image handler.
        
        Args:
            extract_quality: JPEG quality for saving (1-100)
            max_dimension: Maximum width/height for resizing (None = no resize)
        """
        self.logger = logging.getLogger(__name__)
        self.extract_quality = extract_quality
        self.max_dimension = max_dimension
    
    def extract_images(self, file_path: str) -> List[ExtractedImage]:
        """Extract all images from DOCX file."""
        if not Document:
            self.logger.warning("python-docx not available for image extraction")
            return []
        
        try:
            doc = Document(file_path)
            return self._extract_document_images(doc)
        except Exception as e:
            self.logger.error(f"Error extracting images: {e}")
            return []
    
    def extract_and_save_images(self, file_path: str, output_dir: Path) -> Dict[str, str]:
        """Extract images and save to directory.
        
        Returns:
            Mapping of image_id to saved file path
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        images = self.extract_images(file_path)
        
        saved_images = {}
        for img in images:
            try:
                saved_path = img.save(output_dir, quality=self.extract_quality)
                saved_images[img.info.image_id] = str(saved_path)
            except Exception as e:
                self.logger.error(f"Error saving image {img.info.image_id}: {e}")
        
        return saved_images
    
    def _extract_document_images(self, doc: Any) -> List[ExtractedImage]:
        """Extract images from document."""
        images = []
        image_parts = self._get_image_parts(doc)
        
        # Track which images are used in the document
        used_images = set()
        
        # Process inline images in paragraphs
        for para_idx, paragraph in enumerate(doc.paragraphs):
            if hasattr(paragraph, '_element'):
                # Find inline images
                for run_idx, run in enumerate(paragraph.runs):
                    if hasattr(run, '_element'):
                        inline_images = self._find_inline_images(run._element)
                        for img_rel_id in inline_images:
                            if img_rel_id in image_parts:
                                used_images.add(img_rel_id)
                                image_data = image_parts[img_rel_id]
                                extracted = self._process_image(
                                    image_data,
                                    img_rel_id,
                                    para_idx=para_idx,
                                    run_idx=run_idx
                                )
                                if extracted:
                                    # Try to get alt text
                                    alt_text = self._extract_alt_text(run._element)
                                    if alt_text:
                                        extracted.info.alt_text = alt_text
                                    images.append(extracted)
        
        # Process images in tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para_idx, paragraph in enumerate(cell.paragraphs):
                        if hasattr(paragraph, '_element'):
                            for run_idx, run in enumerate(paragraph.runs):
                                if hasattr(run, '_element'):
                                    inline_images = self._find_inline_images(run._element)
                                    for img_rel_id in inline_images:
                                        if img_rel_id in image_parts:
                                            used_images.add(img_rel_id)
                                            image_data = image_parts[img_rel_id]
                                            extracted = self._process_image(
                                                image_data,
                                                img_rel_id,
                                                para_idx=para_idx,
                                                run_idx=run_idx
                                            )
                                            if extracted:
                                                images.append(extracted)
        
        # Optionally include unused images (headers, footers, etc.)
        for rel_id, image_data in image_parts.items():
            if rel_id not in used_images:
                extracted = self._process_image(image_data, rel_id)
                if extracted:
                    images.append(extracted)
        
        return images
    
    def _get_image_parts(self, doc: Any) -> Dict[str, Tuple[str, bytes]]:
        """Get all image parts from document."""
        image_parts = {}
        
        try:
            if hasattr(doc, 'part') and hasattr(doc.part, 'package'):
                package = doc.part.package
                
                # Get document part relationships
                for rel in doc.part.rels.values():
                    if "image" in rel.reltype:
                        image_part = rel.target_part
                        if hasattr(image_part, 'blob'):
                            content_type = getattr(image_part, 'content_type', 'image/unknown')
                            image_parts[rel.rId] = (content_type, image_part.blob)
                
                # Also check for images in other parts (headers, footers)
                for part in package.parts:
                    if hasattr(part, 'rels'):
                        for rel in part.rels.values():
                            if "image" in rel.reltype and rel.rId not in image_parts:
                                image_part = rel.target_part
                                if hasattr(image_part, 'blob'):
                                    content_type = getattr(image_part, 'content_type', 'image/unknown')
                                    image_parts[rel.rId] = (content_type, image_part.blob)
        
        except Exception as e:
            self.logger.debug(f"Error getting image parts: {e}")
        
        return image_parts
    
    def _find_inline_images(self, element: Any) -> List[str]:
        """Find inline image references in an element."""
        image_ids = []
        
        try:
            # Look for drawing elements
            drawings = element.xpath('.//w:drawing')
            for drawing in drawings:
                # Find blip elements which contain image references
                blips = drawing.xpath('.//a:blip', namespaces={
                    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'
                })
                for blip in blips:
                    embed_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                    if embed_id:
                        image_ids.append(embed_id)
        except Exception as e:
            self.logger.debug(f"Error finding inline images: {e}")
        
        return image_ids
    
    def _extract_alt_text(self, element: Any) -> Optional[str]:
        """Extract alt text from drawing element."""
        try:
            # Look for docPr element which contains alt text
            doc_props = element.xpath('.//wp:docPr', namespaces={
                'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
            })
            for prop in doc_props:
                descr = prop.get('descr')
                if descr:
                    return descr
        except Exception as e:
            self.logger.debug(f"Error extracting alt text: {e}")
        
        return None
    
    def _process_image(self, image_data: Tuple[str, bytes], rel_id: str,
                      para_idx: Optional[int] = None, 
                      run_idx: Optional[int] = None) -> Optional[ExtractedImage]:
        """Process and create ExtractedImage object."""
        content_type, data = image_data
        
        try:
            # Calculate hash for deduplication
            hash_val = hashlib.sha256(data).hexdigest()
            
            # Generate filename
            ext = self._get_extension_from_content_type(content_type)
            filename = f"image_{rel_id}{ext}"
            
            # Get image dimensions
            width, height = 0, 0
            pil_image = None
            
            if Image:
                try:
                    pil_image = Image.open(BytesIO(data))
                    width, height = pil_image.size
                    
                    # Resize if needed
                    if self.max_dimension and (width > self.max_dimension or height > self.max_dimension):
                        pil_image.thumbnail((self.max_dimension, self.max_dimension), Image.Resampling.LANCZOS)
                        # Re-save to bytes
                        buffer = BytesIO()
                        if content_type == 'image/jpeg':
                            pil_image.save(buffer, 'JPEG', quality=self.extract_quality)
                        else:
                            pil_image.save(buffer, pil_image.format)
                        data = buffer.getvalue()
                        width, height = pil_image.size
                except Exception as e:
                    self.logger.warning(f"Could not process image with PIL: {e}")
            
            # Create image info
            info = ImageInfo(
                image_id=rel_id,
                original_name=filename,
                content_type=content_type,
                width=width,
                height=height,
                file_size=len(data),
                hash=hash_val,
                paragraph_index=para_idx,
                run_index=run_idx
            )
            
            return ExtractedImage(info=info, data=data, pil_image=pil_image)
            
        except Exception as e:
            self.logger.error(f"Error processing image {rel_id}: {e}")
            return None
    
    def _get_extension_from_content_type(self, content_type: str) -> str:
        """Get file extension from content type."""
        extensions = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/bmp': '.bmp',
            'image/tiff': '.tiff',
            'image/webp': '.webp',
            'image/svg+xml': '.svg'
        }
        return extensions.get(content_type, '.bin')


class ImageManifest:
    """Create and manage image manifest."""
    
    @staticmethod
    def create_manifest(images: List[ExtractedImage]) -> Dict[str, Any]:
        """Create a manifest of extracted images."""
        manifest = {
            'total_images': len(images),
            'total_size': sum(img.info.file_size for img in images),
            'unique_images': len(set(img.info.hash for img in images)),
            'images': []
        }
        
        for img in images:
            img_data = img.info.to_dict()
            # Add location info
            if img.info.paragraph_index is not None:
                img_data['location'] = {
                    'paragraph': img.info.paragraph_index,
                    'run': img.info.run_index
                }
            manifest['images'].append(img_data)
        
        return manifest
    
    @staticmethod
    def save_manifest(manifest: Dict[str, Any], output_path: Path) -> None:
        """Save manifest to JSON file."""
        import json
        
        manifest_path = output_path / 'image_manifest.json'
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)