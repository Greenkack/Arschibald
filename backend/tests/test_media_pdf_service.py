"""
Tests for Media PDF Service

Tests image and photo PDF byte generation functionality.

Requirements: 14.8
Task: 227
"""

import pytest
import io
from pathlib import Path
from PIL import Image

from backend.services.media_pdf_service import (
    MediaPDFService,
    ImageMetadata,
    ImageOptimizer,
    image_to_pdf_bytes,
    photo_to_pdf_bytes,
    multi_image_pdf,
    image_gallery_pdf,
    REPORTLAB_AVAILABLE,
    PIL_AVAILABLE
)


# Skip all tests if required libraries not available
pytestmark = pytest.mark.skipif(
    not (REPORTLAB_AVAILABLE and PIL_AVAILABLE),
    reason="reportlab and Pillow required for media PDF tests"
)


@pytest.fixture
def test_image():
    """Create a test image"""
    img = Image.new('RGB', (800, 600), color='blue')
    return img


@pytest.fixture
def test_image_path(tmp_path, test_image):
    """Save test image to temporary file"""
    img_path = tmp_path / "test_image.jpg"
    test_image.save(img_path, 'JPEG')
    return img_path


@pytest.fixture
def test_images_paths(tmp_path):
    """Create multiple test images"""
    paths = []
    colors = ['red', 'green', 'blue', 'yellow']
    
    for i, color in enumerate(colors):
        img = Image.new('RGB', (640, 480), color=color)
        img_path = tmp_path / f"test_image_{i}.jpg"
        img.save(img_path, 'JPEG')
        paths.append(img_path)
    
    return paths


@pytest.fixture
def service():
    """Create MediaPDFService instance"""
    return MediaPDFService()


class TestImageMetadata:
    """Test ImageMetadata class"""
    
    def test_create_metadata(self):
        """Test creating image metadata"""
        metadata = ImageMetadata(
            filename="test.jpg",
            width=800,
            height=600,
            format="JPEG",
            mode="RGB",
            size_bytes=102400
        )
        
        assert metadata.filename == "test.jpg"
        assert metadata.width == 800
        assert metadata.height == 600
        assert metadata.format == "JPEG"
    
    def test_to_dict(self):
        """Test converting metadata to dictionary"""
        metadata = ImageMetadata(
            filename="test.jpg",
            width=800,
            height=600,
            format="JPEG",
            mode="RGB",
            size_bytes=102400
        )
        
        data = metadata.to_dict()
        
        assert data['filename'] == "test.jpg"
        assert data['width'] == 800
        assert data['height'] == 600
        assert 'size_mb' in data
    
    def test_get_dimensions_str(self):
        """Test getting dimensions as string"""
        metadata = ImageMetadata(
            filename="test.jpg",
            width=800,
            height=600,
            format="JPEG",
            mode="RGB",
            size_bytes=102400
        )
        
        dims = metadata.get_dimensions_str()
        assert dims == "800 x 600 px"
    
    def test_get_aspect_ratio(self):
        """Test calculating aspect ratio"""
        metadata = ImageMetadata(
            filename="test.jpg",
            width=1920,
            height=1080,
            format="JPEG",
            mode="RGB",
            size_bytes=102400
        )
        
        ratio = metadata.get_aspect_ratio()
        assert abs(ratio - 1.777) < 0.01


class TestImageOptimizer:
    """Test ImageOptimizer class"""
    
    def test_optimize_for_pdf(self, test_image):
        """Test image optimization"""
        optimizer = ImageOptimizer()
        optimized = optimizer.optimize_for_pdf(test_image)
        
        assert optimized is not None
        assert optimized.mode == 'RGB'
    
    def test_optimize_large_image(self):
        """Test optimizing large image"""
        large_img = Image.new('RGB', (4000, 3000), color='red')
        optimizer = ImageOptimizer()
        
        optimized = optimizer.optimize_for_pdf(large_img, max_width=1920, max_height=1080)
        
        assert optimized.width <= 1920
        assert optimized.height <= 1080
    
    def test_compress_image(self, test_image):
        """Test image compression"""
        optimizer = ImageOptimizer()
        compressed = optimizer.compress_image(test_image, quality=85)
        
        assert isinstance(compressed, bytes)
        assert len(compressed) > 0


class TestMediaPDFService:
    """Test MediaPDFService class"""
    
    def test_service_initialization(self, service):
        """Test service initialization"""
        assert service is not None
        assert service.engine is not None
        assert service.optimizer is not None
    
    def test_image_to_pdf_bytes(self, service, test_image_path):
        """Test converting single image to PDF"""
        pdf_bytes = service.image_to_pdf_bytes(test_image_path)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_image_to_pdf_with_metadata(self, service, test_image_path):
        """Test image to PDF with metadata included"""
        pdf_bytes = service.image_to_pdf_bytes(
            test_image_path,
            include_metadata=True
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_image_to_pdf_without_optimization(self, service, test_image_path):
        """Test image to PDF without optimization"""
        pdf_bytes = service.image_to_pdf_bytes(
            test_image_path,
            optimize=False
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_photo_to_pdf_bytes(self, service, test_image_path):
        """Test converting photo to PDF"""
        pdf_bytes = service.photo_to_pdf_bytes(
            test_image_path,
            title="Test Photo",
            description="This is a test photo"
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_multi_image_pdf_one_per_page(self, service, test_images_paths):
        """Test multi-image PDF with one per page layout"""
        pdf_bytes = service.multi_image_pdf(
            test_images_paths,
            title="Test Collection",
            layout="one_per_page"
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_multi_image_pdf_two_per_page(self, service, test_images_paths):
        """Test multi-image PDF with two per page layout"""
        pdf_bytes = service.multi_image_pdf(
            test_images_paths,
            title="Test Collection",
            layout="two_per_page"
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_multi_image_pdf_grid(self, service, test_images_paths):
        """Test multi-image PDF with grid layout"""
        pdf_bytes = service.multi_image_pdf(
            test_images_paths,
            title="Test Collection",
            layout="grid"
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_image_gallery_pdf(self, service, test_images_paths):
        """Test image gallery PDF generation"""
        images = [
            {
                'path': str(path),
                'title': f"Image {i+1}",
                'description': f"Description for image {i+1}"
            }
            for i, path in enumerate(test_images_paths)
        ]
        
        pdf_bytes = service.image_gallery_pdf(
            images,
            gallery_title="Test Gallery"
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_extract_image_metadata(self, service, test_image_path):
        """Test extracting image metadata"""
        image = Image.open(test_image_path)
        metadata = service._extract_image_metadata(image, "test.jpg")
        
        assert metadata.filename == "test.jpg"
        assert metadata.width > 0
        assert metadata.height > 0
        assert metadata.format != "unknown"


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    def test_image_to_pdf_bytes_function(self, test_image_path):
        """Test image_to_pdf_bytes convenience function"""
        pdf_bytes = image_to_pdf_bytes(test_image_path)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_image_to_pdf_bytes_with_title(self, test_image_path):
        """Test with custom title"""
        pdf_bytes = image_to_pdf_bytes(
            test_image_path,
            title="Custom Title"
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_photo_to_pdf_bytes_function(self, test_image_path):
        """Test photo_to_pdf_bytes convenience function"""
        pdf_bytes = photo_to_pdf_bytes(
            test_image_path,
            title="Test Photo",
            description="Test description"
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_multi_image_pdf_function(self, test_images_paths):
        """Test multi_image_pdf convenience function"""
        pdf_bytes = multi_image_pdf(
            test_images_paths,
            title="Test Collection"
        )
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_image_gallery_pdf_function(self, test_images_paths):
        """Test image_gallery_pdf convenience function"""
        images = [
            {'path': str(path), 'title': f"Image {i+1}"}
            for i, path in enumerate(test_images_paths)
        ]
        
        pdf_bytes = image_gallery_pdf(images)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_invalid_layout(self, service, test_images_paths):
        """Test with invalid layout"""
        with pytest.raises(ValueError):
            service.multi_image_pdf(
                test_images_paths,
                layout="invalid_layout"
            )
    
    def test_empty_image_list(self, service):
        """Test with empty image list"""
        # Should handle gracefully
        pdf_bytes = service.multi_image_pdf([], title="Empty")
        assert isinstance(pdf_bytes, bytes)
    
    def test_single_image_in_gallery(self, service, test_image_path):
        """Test gallery with single image"""
        images = [{'path': str(test_image_path), 'title': "Single"}]
        pdf_bytes = service.image_gallery_pdf(images)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


class TestImageFormats:
    """Test different image formats"""
    
    def test_png_image(self, service, tmp_path):
        """Test PNG image"""
        img = Image.new('RGB', (640, 480), color='green')
        img_path = tmp_path / "test.png"
        img.save(img_path, 'PNG')
        
        pdf_bytes = service.image_to_pdf_bytes(img_path)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
    
    def test_rgba_image(self, service, tmp_path):
        """Test RGBA image (with transparency)"""
        img = Image.new('RGBA', (640, 480), color=(255, 0, 0, 128))
        img_path = tmp_path / "test_rgba.png"
        img.save(img_path, 'PNG')
        
        pdf_bytes = service.image_to_pdf_bytes(img_path)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
