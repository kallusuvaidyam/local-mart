import io
from PIL import Image

import cloudinary
import cloudinary.uploader
from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)

MAX_DIMENSION = 800
WEBP_QUALITY = 80


def compress_image(file_bytes: bytes) -> bytes:
    """Compress and convert image to WebP before uploading.

    - Resize to max 800x800 (keeping aspect ratio)
    - Convert to WebP format (best compression)
    - Strip EXIF metadata (saves space + privacy)
    """
    img = Image.open(io.BytesIO(file_bytes))

    # Convert RGBA/P to RGB (WebP supports transparency but keeps size small with RGB)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Resize if larger than MAX_DIMENSION
    img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    # Save as WebP with quality optimization
    buffer = io.BytesIO()
    img.save(buffer, format="WEBP", quality=WEBP_QUALITY, optimize=True)
    buffer.seek(0)
    return buffer.read()


def upload_image(file_bytes: bytes, folder: str = "products") -> str:
    """Compress image locally, then upload to Cloudinary."""
    compressed = compress_image(file_bytes)
    result = cloudinary.uploader.upload(
        compressed,
        folder=folder,
        resource_type="image",
        format="webp",
    )
    return result.get("secure_url", "")


def delete_image(public_id: str) -> None:
    cloudinary.uploader.destroy(public_id)
