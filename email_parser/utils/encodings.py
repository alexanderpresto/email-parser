"""
Encoding utility functions for the email parser.
"""
import base64
import binascii
import logging
import quopri
from typing import Optional, Union

from email_parser.exceptions.parsing_exceptions import EncodingError

logger = logging.getLogger(__name__)


def decode_content(
    content: bytes, 
    charset: str = "utf-8", 
    encoding: Optional[str] = None
) -> Union[str, bytes]:
    """
    Decode content based on the specified encoding and charset.
    
    Args:
        content: Content to decode
        charset: Character set for text decoding
        encoding: Transfer encoding (base64, quoted-printable, etc.)
        
    Returns:
        Decoded content as string for text, bytes for binary
        
    Raises:
        EncodingError: If decoding fails
    """
    try:
        # Handle transfer encoding if specified
        if encoding:
            content = decode_transfer_encoding(content, encoding)
            
        # Try to decode as text if not in a binary content type
        try:
            return content.decode(charset)
        except (UnicodeDecodeError, LookupError):
            # If decoding as text fails, try common fallback encodings
            for fallback_charset in ["utf-8", "iso-8859-1", "ascii", "cp1252"]:
                if fallback_charset != charset:
                    try:
                        return content.decode(fallback_charset)
                    except (UnicodeDecodeError, LookupError):
                        continue
                        
            # If all decodings fail, return as bytes
            logger.warning(
                f"Failed to decode content as text with charset {charset}, returning as bytes"
            )
            return content
            
    except Exception as e:
        raise EncodingError(f"Failed to decode content: {str(e)}", charset)


def decode_transfer_encoding(content: bytes, encoding: str) -> bytes:
    """
    Decode content based on transfer encoding.
    
    Args:
        content: Content to decode
        encoding: Transfer encoding type
        
    Returns:
        Decoded content as bytes
        
    Raises:
        EncodingError: If decoding fails
    """
    encoding = encoding.lower()
    
    try:
        if encoding == "base64":
            try:
                return base64.b64decode(content)
            except binascii.Error as e:
                # Try to handle malformed base64 by adding padding
                padded = content + b"=" * (4 - (len(content) % 4))
                return base64.b64decode(padded)
                
        elif encoding in ("quoted-printable", "quopri"):
            return quopri.decodestring(content)
            
        elif encoding == "uuencode" or encoding == "uue":
            import uu
            import io
            
            input_file = io.BytesIO(content)
            output_file = io.BytesIO()
            uu.decode(input_file, output_file)
            return output_file.getvalue()
            
        elif encoding == "binhex":
            import binhex
            import io
            import tempfile
            
            # binhex requires file objects
            with tempfile.NamedTemporaryFile(delete=False) as temp_in:
                temp_in.write(content)
                temp_in_name = temp_in.name
                
            with tempfile.NamedTemporaryFile(delete=False) as temp_out:
                temp_out_name = temp_out.name
                
            try:
                binhex.hexbin(temp_in_name, temp_out_name)
                with open(temp_out_name, "rb") as f:
                    return f.read()
            finally:
                try:
                    os.unlink(temp_in_name)
                    os.unlink(temp_out_name)
                except:
                    pass
                    
        else:
            # For unknown encodings, return as-is
            logger.warning(f"Unknown transfer encoding: {encoding}, returning as-is")
            return content
            
    except Exception as e:
        raise EncodingError(f"Failed to decode {encoding} content: {str(e)}", encoding)
        
    return content


def detect_encoding(content: bytes) -> str:
    """
    Try to detect the encoding of content.
    
    Args:
        content: Content to analyze
        
    Returns:
        Best guess of encoding name
    """
    try:
        import chardet
        result = chardet.detect(content)
        if result["confidence"] > 0.7:
            return result["encoding"] or "utf-8"
        return "utf-8"  # Default to UTF-8 if uncertain
    except ImportError:
        # If chardet is not available, try basic detection
        try:
            content.decode("utf-8")
            return "utf-8"
        except UnicodeDecodeError:
            try:
                content.decode("iso-8859-1")
                return "iso-8859-1"
            except UnicodeDecodeError:
                return "utf-8"  # Default to UTF-8 if can't detect