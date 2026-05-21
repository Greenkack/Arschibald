# Product Image Management - Quick Reference

## Quick Start

### Upload Image
```bash
curl -X POST http://localhost:8000/api/v1/images/upload \
  -F "file=@product.jpg" \
  -F "product_id=123" \
  -F "alt_text=Solar Panel" \
  -F "generate_variants=true"
```

### Get Product Images
```bash
curl http://localhost:8000/api/v1/images/product/123
```

### Search Images
```bash
curl -X POST http://localhost:8000/api/v1/images/search \
  -H "Content-Type: application/json" \
  -d '{"query": "solar panel", "limit": 10}'
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/images/upload` | Upload single image |
| POST | `/images/bulk-upload` | Upload multiple images |
| POST | `/images/optimize` | Optimize image |
| GET | `/images/{id}` | Get image by ID |
| GET | `/images/product/{id}` | Get product images |
| POST | `/images/search` | Search images |
| PATCH | `/images/{id}` | Update metadata |
| DELETE | `/images/{id}` | Delete image |
| POST | `/images/{id}/set-primary` | Set as primary |
| GET | `/images/{id}/variants` | Get variants |
| POST | `/images/{id}/regenerate-variants` | Regenerate variants |

## Image Variants

| Variant | Size | Use Case |
|---------|------|----------|
| thumbnail | 150x150 | Listings |
| small | 300x300 | Search results |
| medium | 600x600 | Product details |
| large | 1200x1200 | Zoom view |

## Supported Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- GIF (.gif)

**Max file size:** 10MB

## Common Operations

### Set Primary Image
```python
response = requests.post(
    f'/api/v1/images/{image_id}/set-primary',
    params={'product_id': 123}
)
```

### Bulk Upload
```python
files = [
    ('files', open('image1.jpg', 'rb')),
    ('files', open('image2.jpg', 'rb')),
    ('files', open('image3.jpg', 'rb'))
]
response = requests.post(
    '/api/v1/images/bulk-upload',
    files=files,
    data={'product_id': 123}
)
```

### Update Metadata
```python
response = requests.patch(
    f'/api/v1/images/{image_id}',
    json={
        'alt_text': 'Updated text',
        'tags': ['new-tag'],
        'is_active': True
    }
)
```

## Search Filters

```json
{
  "query": "solar panel",
  "product_category": "solar-panels",
  "tags": ["premium"],
  "min_width": 800,
  "max_width": 2000,
  "min_height": 600,
  "max_height": 1500,
  "is_primary_only": false,
  "limit": 50,
  "offset": 0
}
```

## Optimization Options

```json
{
  "image_id": 456,
  "quality": 85,
  "max_width": 1200,
  "max_height": 1200,
  "format": "webp",
  "generate_variants": true
}
```

## CDN Configuration

```python
cdn_config = {
    "provider": "cloudflare",
    "base_url": "https://cdn.example.com",
    "api_key": "your-api-key"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Invalid file format or size |
| 404 | Image not found |
| 409 | Duplicate image (same hash) |
| 413 | File too large (>10MB) |
| 500 | Server error |

## Performance Tips

1. **Use WebP format** for 30-40% smaller files
2. **Enable CDN** for 90% bandwidth reduction
3. **Generate variants** on upload for faster loading
4. **Use lazy loading** in frontend
5. **Set appropriate quality** (85% recommended)

## Database Queries

### Get all images for product
```sql
SELECT * FROM product_images 
WHERE product_id = 123 
AND is_active = TRUE 
ORDER BY display_order, id;
```

### Find primary image
```sql
SELECT * FROM product_images 
WHERE product_id = 123 
AND is_primary = TRUE 
LIMIT 1;
```

### Search by tags
```sql
SELECT * FROM product_images 
WHERE JSON_CONTAINS(tags, '["premium"]');
```

## Frontend Integration

### React Component
```tsx
import { useProductImages } from './hooks/useImages';

function ProductGallery({ productId }) {
  const { images, loading } = useProductImages(productId);
  
  if (loading) return <Spinner />;
  
  return (
    <div className="gallery">
      {images.map(img => (
        <img 
          key={img.id}
          src={img.variants.medium}
          alt={img.alt_text}
          loading="lazy"
        />
      ))}
    </div>
  );
}
```

### Image Upload Hook
```tsx
function useImageUpload() {
  const [uploading, setUploading] = useState(false);
  
  const upload = async (file, options) => {
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      Object.entries(options).forEach(([key, value]) => {
        formData.append(key, value);
      });
      
      const response = await fetch('/api/v1/images/upload', {
        method: 'POST',
        body: formData
      });
      
      return await response.json();
    } finally {
      setUploading(false);
    }
  };
  
  return { upload, uploading };
}
```

## Troubleshooting

### Upload fails
```bash
# Check file size
ls -lh image.jpg

# Check format
file image.jpg

# Test upload
curl -v -X POST http://localhost:8000/api/v1/images/upload \
  -F "file=@image.jpg" \
  -F "product_id=123"
```

### Variants not generated
```bash
# Check PIL installation
python -c "from PIL import Image; print('OK')"

# Check permissions
ls -la uploads/products/

# Regenerate variants
curl -X POST http://localhost:8000/api/v1/images/456/regenerate-variants
```

### Search not working
```bash
# Rebuild search index
python -c "from backend.services.image_service import ImageService; \
           ImageService(db).rebuild_search_index()"
```

## Best Practices

✓ Always set alt text for accessibility  
✓ Use descriptive filenames  
✓ Add relevant tags  
✓ Set one primary image per product  
✓ Enable CDN in production  
✓ Generate variants on upload  
✓ Use WebP format  
✓ Implement lazy loading  
✓ Monitor file sizes  
✓ Regular cleanup of unused images  

## Resources

- Full Guide: `IMAGE_MANAGEMENT_GUIDE.md`
- API Documentation: `/api/v1/docs`
- Demo Script: `backend/demo_image_management.py`
- Migration Script: `backend/migrations/add_image_tables.py`
