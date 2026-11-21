"""
File Storage Service.
Handles saving, retrieving, and managing uploaded images and generated files
with platform-independent path handling and detailed step logging.
"""

import os
import uuid
import logging
from datetime import datetime
from PIL import Image
from werkzeug.utils import secure_filename

from server.utils.image_utils import validate_image_file, resolve_absolute_image_path

logger = logging.getLogger(__name__)


class StorageService:
    """Local file storage for uploaded and generated images."""

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    THUMBNAIL_SIZE = (200, 200)

    def __init__(self, upload_folder):
        """
        Args:
            upload_folder: Base directory for file storage.
        """
        self.upload_folder = os.path.abspath(upload_folder)
        # Requirement 7: Automatically create upload directory if it does not exist
        os.makedirs(self.upload_folder, exist_ok=True)
        logger.info(f"[StorageService] Initialized with upload folder: '{self.upload_folder}'")

    def _allowed_file(self, filename):
        """Check if the file extension is allowed."""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def _get_user_folder(self, user_id):
        """Get or create a user-specific upload directory."""
        user_folder = os.path.join(self.upload_folder, str(user_id or 'anonymous'))
        os.makedirs(user_folder, exist_ok=True)
        return user_folder

    def save_upload(self, file, user_id=None):
        """
        Validate and save an uploaded file to disk.
        Logs every step of upload, directory creation, saving, and existence verification.
        
        Args:
            file: Werkzeug FileStorage object.
            user_id: User's ID string for directory namespacing.
        
        Returns:
            dict: {image_path, thumbnail_path, web_image_url, web_thumb_url, filename}
        Raises:
            ValueError: If image validation fails.
            FileNotFoundError: If saved file is unreadable or missing.
        """
        # Requirement 12 Log: Upload received
        logger.info(f"[StorageService] Upload received for user '{user_id or 'anonymous'}': filename='{file.filename}'")

        is_valid, err_msg = validate_image_file(file)
        if not is_valid:
            logger.error(f"[StorageService] Image validation failed for '{file.filename}': {err_msg}")
            raise ValueError(err_msg)

        # Requirement 7 & 12 Log: Upload directory created (if needed)
        user_folder = self._get_user_folder(user_id)
        logger.info(f"[StorageService] Upload directory created/verified at '{user_folder}'")

        # Generate unique secure filename
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_name = f"{timestamp}_{uuid.uuid4().hex[:8]}.{ext}"
        safe_name = secure_filename(unique_name)

        # Requirement 10 & 11: Use os.path.join for platform-independent path
        image_path = os.path.abspath(os.path.join(user_folder, safe_name))

        # Requirement 12 Log: Image saved & Full saved path
        file.save(image_path)
        logger.info(f"[StorageService] Image saved successfully. Full saved path: '{image_path}'")

        # Requirement 8 & 12 Log: File existence check & readable check
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image saving failed: File does not exist at '{image_path}'")

        if not os.access(image_path, os.R_OK):
            raise PermissionError(f"Image saving failed: File is not readable at '{image_path}'")

        logger.info(f"[StorageService] File existence check passed for '{image_path}'")

        # Generate thumbnail
        thumb_name = f"thumb_{safe_name}"
        thumb_path = os.path.abspath(os.path.join(user_folder, thumb_name))
        self._create_thumbnail(image_path, thumb_path)

        # Requirement 12 Log: Image successfully loaded verification
        try:
            with Image.open(image_path) as img:
                logger.info(f"[StorageService] Image successfully loaded: format='{img.format}', resolution={img.size[0]}x{img.size[1]}px")
        except Exception as e:
            raise ValueError(f"Corrupted image saved to disk at '{image_path}': {str(e)}")

        # Construct web-accessible relative URLs for HTTP clients
        uid_str = str(user_id or 'anonymous')
        web_image_url = f"/uploads/{uid_str}/{safe_name}"
        web_thumb_url = f"/uploads/{uid_str}/{thumb_name}"

        return {
            'image_path': image_path,
            'thumbnail_path': thumb_path,
            'web_image_url': web_image_url,
            'web_thumb_url': web_thumb_url,
            'filename': safe_name
        }

    def save_generated_image(self, image_bytes, user_id, prefix='tryon'):
        """
        Save a generated image to disk.
        """
        user_folder = self._get_user_folder(user_id)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.abspath(os.path.join(user_folder, filename))

        with open(filepath, 'wb') as f:
            f.write(image_bytes)

        logger.info(f"[StorageService] Generated image saved at '{filepath}'")
        return filepath

    def _create_thumbnail(self, source_path, thumb_path):
        """Create a thumbnail version of the image."""
        try:
            with Image.open(source_path) as img:
                img.thumbnail(self.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                img.save(thumb_path)
        except Exception as e:
            logger.warning(f"[StorageService] Thumbnail creation error ({e}), copying original...")
            import shutil
            shutil.copy2(source_path, thumb_path)

    def get_file_path(self, relative_path):
        """Resolve a relative path to an absolute file path."""
        return resolve_absolute_image_path(relative_path, upload_folder=self.upload_folder)

    def delete_file(self, file_path):
        """Delete a file if it exists."""
        resolved = resolve_absolute_image_path(file_path, upload_folder=self.upload_folder)
        if resolved and os.path.exists(resolved):
            os.remove(resolved)
            return True
        return False
